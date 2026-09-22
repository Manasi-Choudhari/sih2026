"""
Direct Neo4j seeder for VAJRA scenarios.
Seeds all 5 scenario fixtures into the sih2026 database.
"""
import json
from pathlib import Path
from ml.db.neo4j_client import get_session

def seed_neo4j_only():
    fixtures_dir = Path('scenarios/fixtures')
    total_nodes = 0
    total_rels = 0

    with get_session() as session:
        # Clear existing demo-seed nodes to avoid duplicates
        session.run('MATCH (n:Demo) DETACH DELETE n')
        print("Cleared existing Demo nodes.")

        for fix_file in sorted(fixtures_dir.glob('scenario_*.json')):
            fix = json.loads(fix_file.read_text(encoding='utf-8'))
            scenario_id = fix.get('scenario_id', fix_file.stem)
            neo = fix.get('neo4j', {})

            for node in neo.get('nodes', []):
                lbl = node['label']
                props = node.get('properties', {})
                # Build dynamic MERGE query
                kv = ", ".join(f"{k}: ${k}" for k in props.keys())
                q = f"MERGE (n:{lbl}:Demo {{{kv}}})"
                session.run(q, **props)
                total_nodes += 1

            for rel in neo.get('relationships', []):
                rtype = rel['type']
                src = rel['from']
                tgt = rel['to']
                fl = rel.get('from_label', 'Wallet')
                tl = rel.get('to_label', 'Wallet')
                props = rel.get('properties', {})

                if fl == 'Wallet':
                    fm = "w1.address = $from_addr"
                else:
                    fm = "w1.name = $from_addr"

                if tl == 'Wallet':
                    tm = "w2.address = $to_addr"
                elif tl == 'VASP':
                    tm = "w2.name = $to_addr"
                elif tl == 'Label':
                    tm = "w2.label_text = $to_addr"
                else:
                    tm = "w2.address = $to_addr"

                if props:
                    pa = ", ".join(f"r.{k} = ${k}" for k in props.keys())
                else:
                    pa = "r.demo = true"

                q = f"""
                MATCH (w1:{fl}), (w2:{tl})
                WHERE {fm} AND {tm}
                MERGE (w1)-[r:{rtype}]->(w2)
                ON CREATE SET {pa}
                """
                session.run(q, from_addr=src, to_addr=tgt, **props)
                total_rels += 1

            print(f"  Seeded scenario: {scenario_id}")

    print(f"\nNeo4j seeding complete: {total_nodes} nodes, {total_rels} relationships.")

if __name__ == "__main__":
    seed_neo4j_only()
