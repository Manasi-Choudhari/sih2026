"""
Seed Neo4j database `sih2026` with VAJRA schema + 5 synthetic scenarios.

Idempotent: clears prior VAJRA demo nodes tagged with demo_seed=true, then reloads.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ml.db.neo4j_client import get_session, ping


CONSTRAINTS = [
    "CREATE CONSTRAINT wallet_address IF NOT EXISTS FOR (w:Wallet) REQUIRE w.address IS UNIQUE",
    "CREATE CONSTRAINT vasp_name IF NOT EXISTS FOR (v:VASP) REQUIRE v.name IS UNIQUE",
]


def _ts(days_ago: float = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


CLEAR = """
MATCH (n)
WHERE n.demo_seed = true
DETACH DELETE n
"""


def seed() -> dict:
    print("ping:", ping())
    with get_session() as session:
        for c in CONSTRAINTS:
            session.run(c)
        session.run(CLEAR)

        # --- Shared VASP + mixer markers ---
        session.run(
            """
            CREATE (v:VASP:Demo {
              name: 'DemoExchange',
              known_addresses: ['s1_vasp'],
              last_verified: $now,
              demo_seed: true
            })
            CREATE (m:Wallet:Demo {
              address: 's4_mixer',
              chain: 'BTC',
              first_seen: $old,
              last_seen: $now,
              cluster_id: 'mixer_cluster',
              entity_type: 'mixer',
              demo_seed: true,
              scenario_id: 'scenario_4_mixer',
              case_id: 'case_s4',
              label_risk: 1
            })
            """,
            now=_ts(0),
            old=_ts(400),
        )

        # Scenario 1 — direct VASP
        session.run(
            """
            MATCH (v:VASP {name:'DemoExchange'})
            CREATE (a:Wallet:Demo {
              address:'s1_victim', chain:'ETH', first_seen:$t2, last_seen:$t1,
              cluster_id:'c_s1', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_1_direct', case_id:'case_s1', label_risk:1
            })
            CREATE (b:Wallet:Demo {
              address:'s1_hop1', chain:'ETH', first_seen:$t1, last_seen:$t0,
              cluster_id:'c_s1', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_1_direct', case_id:'case_s1', label_risk:1
            })
            CREATE (c:Wallet:Demo {
              address:'s1_vasp', chain:'ETH', first_seen:$old, last_seen:$t0,
              cluster_id:'vasp_demo', entity_type:'vasp', demo_seed:true,
              scenario_id:'scenario_1_direct', case_id:'case_s1', label_risk:0
            })
            CREATE (d:Wallet:Demo {
              address:'s1_cold', chain:'ETH', first_seen:$old, last_seen:$old,
              cluster_id:'c_cold', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_1_direct', case_id:'case_s1', label_risk:0
            })
            CREATE (a)-[:TRANSACTION {
              tx_hash:'s1_tx1', chain:'ETH', block_height:100, timestamp:$t2,
              amount:2.5, asset:'ETH', direction:'out', is_bridge_leg:false,
              confidence_of_link:0.99, demo_seed:true
            }]->(b)
            CREATE (b)-[:TRANSACTION {
              tx_hash:'s1_tx2', chain:'ETH', block_height:101, timestamp:$t1,
              amount:2.48, asset:'ETH', direction:'out', is_bridge_leg:false,
              confidence_of_link:0.99, demo_seed:true
            }]->(c)
            CREATE (c)-[:LABELED_AS {confidence_tier:'Strong', demo_seed:true}]->(v)
            CREATE (lab:Label:Demo {
              source:'official', label_text:'DemoExchange deposit',
              confidence:0.99, first_seen:$old, last_verified:$t0, demo_seed:true
            })
            CREATE (c)-[:HAS_LABEL {demo_seed:true}]->(lab)
            """,
            t0=_ts(0.01),
            t1=_ts(0.02),
            t2=_ts(0.03),
            old=_ts(200),
        )

        # Scenario 2 — peel chain
        session.run(
            """
            UNWIND range(0,3) AS i
            WITH i, 3.0 - i * 0.4 AS amt
            CREATE (w:Wallet:Demo {
              address: 's2_peel_' + toString(i),
              chain: 'BTC',
              first_seen: datetime() - duration({hours: i}),
              last_seen: datetime(),
              cluster_id: 'c_peel',
              entity_type: 'eoa',
              demo_seed: true,
              scenario_id: 'scenario_2_peel',
              case_id: 'case_s2',
              label_risk: 1,
              peel_hint: 0.85 + i * 0.01
            })
            WITH collect(w) AS wallets
            UNWIND range(0, size(wallets)-2) AS i
            WITH wallets[i] AS a, wallets[i+1] AS b, i
            CREATE (a)-[:TRANSACTION {
              tx_hash: 's2_tx_' + toString(i),
              chain: 'BTC', block_height: 200 + i,
              timestamp: datetime() - duration({minutes: 30 - i}),
              amount: 2.7 - i * 0.4, asset: 'BTC', direction: 'out',
              is_bridge_leg: false, confidence_of_link: 0.9, demo_seed: true
            }]->(b)
            """
        )
        session.run(
            """
            CREATE (n:Wallet:Demo {
              address:'s2_normal', chain:'BTC', first_seen:$old, last_seen:$now,
              cluster_id:'c_norm', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_2_peel', case_id:'case_s2', label_risk:0
            })
            CREATE (n)-[:TRANSACTION {
              tx_hash:'s2_norm_tx', chain:'BTC', block_height:50, timestamp:$old,
              amount:0.15, asset:'BTC', direction:'out', is_bridge_leg:false,
              confidence_of_link:0.8, demo_seed:true
            }]->(n)
            """,
            old=_ts(10),
            now=_ts(0),
        )

        # Scenario 3 — cross-chain bridge
        session.run(
            """
            CREATE (btc:Wallet:Demo {
              address:'s3_btc_lock', chain:'BTC', first_seen:$t1, last_seen:$t1,
              cluster_id:'c_bridge', entity_type:'bridge_leg', demo_seed:true,
              scenario_id:'scenario_3_cross_chain', case_id:'case_s3', label_risk:1
            })
            CREATE (eth:Wallet:Demo {
              address:'s3_eth_mint', chain:'ETH', first_seen:$t0, last_seen:$t0,
              cluster_id:'c_bridge', entity_type:'bridge_leg', demo_seed:true,
              scenario_id:'scenario_3_cross_chain', case_id:'case_s3', label_risk:1
            })
            CREATE (ben:Wallet:Demo {
              address:'s3_benign', chain:'ETH', first_seen:$old, last_seen:$old,
              cluster_id:'c_b3', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_3_cross_chain', case_id:'case_s3', label_risk:0
            })
            CREATE (btc)-[:TRANSACTION {
              tx_hash:'s3_lock', chain:'BTC', block_height:300, timestamp:$t1,
              amount:1.2, asset:'BTC', direction:'out', is_bridge_leg:true,
              confidence_of_link:0.7, demo_seed:true
            }]->(btc)
            CREATE (eth)-[:TRANSACTION {
              tx_hash:'s3_mint', chain:'ETH', block_height:301, timestamp:$t0,
              amount:1.18, asset:'ETH', direction:'in', is_bridge_leg:true,
              confidence_of_link:0.7, demo_seed:true
            }]->(eth)
            CREATE (btc)-[:CROSS_CHAIN_LINK {
              source_chain_tx:'s3_lock', dest_chain_tx:'s3_mint',
              bridge_contract:'demo_bridge',
              correlation_method:'amount_time_asset',
              correlation_confidence:0.55, demo_seed:true
            }]->(eth)
            CREATE (ben)-[:TRANSACTION {
              tx_hash:'s3_ben', chain:'ETH', block_height:10, timestamp:$old,
              amount:0.04, asset:'ETH', direction:'out', is_bridge_leg:false,
              confidence_of_link:0.9, demo_seed:true
            }]->(ben)
            """,
            t0=_ts(0.05),
            t1=_ts(0.1),
            old=_ts(20),
        )

        # Scenario 4 — mixer boundary
        session.run(
            """
            MATCH (m:Wallet {address:'s4_mixer'})
            CREATE (p:Wallet:Demo {
              address:'s4_pre_mixer', chain:'BTC', first_seen:$t1, last_seen:$t0,
              cluster_id:'c_m4', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_4_mixer', case_id:'case_s4', label_risk:1
            })
            CREATE (q:Wallet:Demo {
              address:'s4_quiet', chain:'BTC', first_seen:$old, last_seen:$old,
              cluster_id:'c_q4', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_4_mixer', case_id:'case_s4', label_risk:0
            })
            CREATE (p)-[:TRANSACTION {
              tx_hash:'s4_in', chain:'BTC', block_height:400, timestamp:$t0,
              amount:4.0, asset:'BTC', direction:'out', is_bridge_leg:false,
              confidence_of_link:0.95, demo_seed:true
            }]->(m)
            // fan-out from mixer
            UNWIND range(1,5) AS i
            CREATE (o:Wallet:Demo {
              address:'s4_out_' + toString(i), chain:'BTC',
              first_seen:$t0, last_seen:$t0, cluster_id:'c_mout',
              entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_4_mixer', case_id:'case_s4', label_risk:1
            })
            CREATE (m)-[:TRANSACTION {
              tx_hash:'s4_out_tx_' + toString(i), chain:'BTC', block_height:401,
              timestamp:$t0, amount:0.8, asset:'BTC', direction:'out',
              is_bridge_leg:false, confidence_of_link:0.6, demo_seed:true
            }]->(o)
            """,
            t0=_ts(0.01),
            t1=_ts(1),
            old=_ts(30),
        )

        # Scenario 5 — conflicting labels
        session.run(
            """
            CREATE (w:Wallet:Demo {
              address:'s5_conflict', chain:'ETH', first_seen:$t0, last_seen:$t0,
              cluster_id:'c_s5', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_5_conflicting', case_id:'case_s5', label_risk:1
            })
            CREATE (c:Wallet:Demo {
              address:'s5_clean_label', chain:'ETH', first_seen:$old, last_seen:$t0,
              cluster_id:'c_s5b', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_5_conflicting', case_id:'case_s5', label_risk:0
            })
            CREATE (l1:Label:Demo {
              source:'crowdsource', label_text:'exchange_A', confidence:0.4,
              first_seen:$old, last_verified:$old, demo_seed:true
            })
            CREATE (l2:Label:Demo {
              source:'crowdsource', label_text:'exchange_B', confidence:0.4,
              first_seen:$old, last_verified:$t0, demo_seed:true
            })
            CREATE (l3:Label:Demo {
              source:'official', label_text:'known_good', confidence:0.9,
              first_seen:$old, last_verified:$t0, demo_seed:true
            })
            CREATE (w)-[:HAS_LABEL {demo_seed:true}]->(l1)
            CREATE (w)-[:HAS_LABEL {demo_seed:true}]->(l2)
            CREATE (c)-[:HAS_LABEL {demo_seed:true}]->(l3)
            CREATE (w)-[:TRANSACTION {
              tx_hash:'s5_tx', chain:'ETH', block_height:500, timestamp:$t0,
              amount:1.4, asset:'ETH', direction:'out', is_bridge_leg:false,
              confidence_of_link:0.8, demo_seed:true
            }]->(c)
            """,
            t0=_ts(0.2),
            old=_ts(90),
        )

        # Dormant activation extras
        session.run(
            """
            CREATE (h:Wallet:Demo {
              address:'s_dormant_hot', chain:'ETH', first_seen:$old, last_seen:$t0,
              cluster_id:'c_dorm', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_dormant', case_id:'case_extra', label_risk:1,
              dormant_days: 365.0
            })
            CREATE (cold:Wallet:Demo {
              address:'s_dormant_cold', chain:'ETH', first_seen:$old, last_seen:$old,
              cluster_id:'c_dorm2', entity_type:'eoa', demo_seed:true,
              scenario_id:'scenario_dormant', case_id:'case_extra', label_risk:0,
              dormant_days: 365.0
            })
            CREATE (h)-[:TRANSACTION {
              tx_hash:'dorm_tx', chain:'ETH', block_height:600, timestamp:$t0,
              amount:8.0, asset:'ETH', direction:'out', is_bridge_leg:false,
              confidence_of_link:0.9, demo_seed:true
            }]->(cold)
            """,
            t0=_ts(0.01),
            old=_ts(365),
        )

        counts = session.run(
            """
            MATCH (n:Demo)
            RETURN labels(n)[0] AS label, count(*) AS c
            ORDER BY c DESC
            """
        ).data()
        rels = session.run(
            """
            MATCH (:Demo)-[r]->()
            RETURN type(r) AS t, count(*) AS c
            ORDER BY c DESC
            """
        ).data()

    return {"nodes": counts, "rels": rels}


if __name__ == "__main__":
    info = seed()
    print("Seed complete:", info)
