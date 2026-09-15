// /frontend/lib/scenarios/fixtures.ts
// Single source of truth for the 5 synthetic fixture scenarios + reference case.
// Enables Task 2 (Scenario visual shell) and seamless demo walkthroughs.

import type {
  CaseSummary,
  GraphData,
  AttributionResult,
  AtlasResult,
  EvidenceRecord,
  QueueCaseItem,
  RecommendationItem,
} from "../api/types";

export interface ScenarioBundle {
  summary: CaseSummary;
  graph: GraphData;
  attribution: AttributionResult;
  atlas: AtlasResult;
  evidence: EvidenceRecord[];
  recommendation: RecommendationItem;
}

// ---------------------------------------------------------------------------
// 1. Scenario 1: Direct VASP Attribution (Binance / DemoExchange, ETH)
// ---------------------------------------------------------------------------
const scenario1: ScenarioBundle = {
  summary: {
    case_id: "CASE-2026-0001",
    scenario_id: "scenario_1_direct",
    status: "open",
    created_at: "2026-09-10T12:00:00Z",
    reported_at_display: "1 day ago",
    amount_inr: "₹2,10,000",
    crypto_amount: "2.5 ETH",
    complaint_ref: "NCRP complaint #91024",
    pattern_summary: "Direct hop to regulated exchange",
    metrics: {
      rule_risk_score: 0.85,
      attribution_confidence: 0.94,
      ml_probability: 0.82,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "direct_deposit_to_known_vasp", importance: 0.68 },
          { feature: "swift_forwarding_speed_min", importance: 0.22 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
    leading_candidate: {
      candidate_id: "cand-s1-01",
      vasp_name: "DemoExchange (Regulated Custody)",
      branch_id: "branch-1",
      evidence_tier: "Strong",
      supporting_evidence: [
        "Direct 1-hop path from victim to verified active deposit address",
        "Recent on-chain activity matches exchange hot-wallet sweep pattern",
        "Official VASP directory confirmation within 24 hours",
      ],
      contradicting_evidence: [],
      unknowns: ["Customer account identifier held by exchange"],
      labels: [
        { source: "official_fi_registry", freshness: "2026-09-10", confidence_tier: "Strong" },
        { source: "chain_analytics_core", freshness: "2026-09-08", confidence_tier: "Strong" },
      ],
      path_directness_score: 0.98,
      corroboration_score: 0.95,
    },
  },
  graph: {
    case_id: "CASE-2026-0001",
    nodes: [
      { id: "s1_victim", address: "0x71C...victim", chain: "ETH", kind: "wallet", label: "Victim Wallet", is_terminal: false, amount: 2.5 },
      { id: "s1_hop1", address: "0x3dA...hop1", chain: "ETH", kind: "wallet", label: "Layering Hop 1", is_terminal: false, amount: 2.5 },
      { id: "s1_vasp", address: "0x98f...vasp", chain: "ETH", kind: "vasp", label: "DemoExchange Hot Wallet", evidence_tier: "Strong", is_terminal: true, amount: 2.48 },
    ],
    edges: [
      { id: "s1_e1", source: "s1_victim", target: "s1_hop1", type: "TRANSACTION", amount: 2.5, asset: "ETH", timestamp: "2026-09-10T12:05:00Z", hop_index: 0, tx_hash: "s1_tx1", value_retained_pct: 1.0 },
      { id: "s1_e2", source: "s1_hop1", target: "s1_vasp", type: "TRANSACTION", amount: 2.48, asset: "ETH", timestamp: "2026-09-10T14:30:00Z", hop_index: 1, tx_hash: "s1_tx2", value_retained_pct: 0.99 },
    ],
    termination_reason: "known_service_boundary",
  },
  attribution: {
    case_id: "CASE-2026-0001",
    candidates: [
      {
        candidate_id: "cand-s1-01",
        vasp_name: "DemoExchange (Regulated Custody)",
        branch_id: "branch-1",
        evidence_tier: "Strong",
        supporting_evidence: [
          "Direct 1-hop path from victim to verified active deposit address",
          "Recent on-chain activity matches exchange hot-wallet sweep pattern",
          "Official VASP directory confirmation within 24 hours",
        ],
        contradicting_evidence: [],
        unknowns: ["Customer account identifier held by exchange"],
        labels: [
          { source: "official_fi_registry", freshness: "2026-09-10", confidence_tier: "Strong" },
          { source: "chain_analytics_core", freshness: "2026-09-08", confidence_tier: "Strong" },
        ],
        path_directness_score: 0.98,
        corroboration_score: 0.95,
      },
    ],
    patterns: [
      {
        pattern: "rapid_forwarding",
        label: "Rapid Forwarding",
        explanation: "Funds forwarded to deposit address within 2.5 hours of initial complaint transfer.",
        branch_id: "branch-1",
      },
    ],
    metrics: {
      rule_risk_score: 0.85,
      attribution_confidence: 0.94,
      ml_probability: 0.82,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "direct_deposit_to_known_vasp", importance: 0.68 },
          { feature: "swift_forwarding_speed_min", importance: 0.22 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
  },
  atlas: {
    case_id: "CASE-2026-0001",
    alternatives: [
      { hypothesis: "Intermediary address (s1_hop1) is a third-party non-custodial OTC settlement relay.", plausibility: 0.12 },
    ],
    contradictions: [],
    missing_data: ["Exchange confirmation of beneficiary KYC details under Section 91 CrPC."],
    robustness_score: 0.88,
  },
  evidence: [
    { record_id: "rec-s1-001", case_id: "CASE-2026-0001", record_type: "case_created", content_hash: "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0", previous_hash: "GENESIS", created_at: "2026-09-10T12:00:00Z", status: "PASS" },
    { record_id: "rec-s1-002", case_id: "CASE-2026-0001", record_type: "trace_hop", content_hash: "b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01a", previous_hash: "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0", created_at: "2026-09-10T12:05:00Z", status: "PASS" },
    { record_id: "rec-s1-003", case_id: "CASE-2026-0001", record_type: "attribution_verdict", content_hash: "c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01a2b", previous_hash: "b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01a", created_at: "2026-09-10T14:35:00Z", status: "PASS" },
  ],
  recommendation: {
    rec_id: "rec-s1-act-01",
    case_id: "CASE-2026-0001",
    finding: "2.48 ETH deposited into DemoExchange hot wallet 0x98f...vasp within 2 hops.",
    target_vasp: "DemoExchange Compliance Unit",
    target_address: "0x98f...vasp",
    suggested_action: "freeze_notice",
    action_title: "Issue Emergency Freeze Notice (Section 91 CrPC)",
    statutory_basis: "Section 91 CrPC r/w Information Technology Act (Simulated NCRP)",
    confidence: 0.94,
    approval_status: "pending",
  },
};

// ---------------------------------------------------------------------------
// 2. Scenario 2 / Reference Case: Peel Chain (CASE-2026-0417, ₹4.2L)
// Directly implements vajra_ui_reference.html and scenario_2_peel.json!
// ---------------------------------------------------------------------------
const scenario2: ScenarioBundle = {
  summary: {
    case_id: "CASE-2026-0417",
    scenario_id: "scenario_2_peel",
    status: "in_review",
    created_at: "2026-09-11T09:12:00Z",
    reported_at_display: "3 days ago",
    amount_inr: "₹4,20,000",
    crypto_amount: "4.2 BTC",
    complaint_ref: "NCRP complaint #88213",
    pattern_summary: "Peel chain + structuring detected",
    metrics: {
      rule_risk_score: 0.72,
      attribution_confidence: 0.65,
      ml_probability: 0.78, // Disagreement trigger!
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "mixer_proximity_score", importance: 0.54 },
          { feature: "repeating_peel_ratio", importance: 0.28 },
          { feature: "structuring_frequency", importance: 0.12 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
    leading_candidate: {
      candidate_id: "cand-s2-01",
      vasp_name: "VASP-X (exchange, verified)",
      branch_id: "branch-1",
      evidence_tier: "Medium",
      supporting_evidence: [
        "Single crowdsourced label, clean multi-hop path",
        "Consistent deposit/withdrawal service pattern",
        "Peel residue retained across hops under 1% threshold",
      ],
      contradicting_evidence: [
        "VASP-X's label was last verified 340 days ago; community report notes dormancy",
      ],
      unknowns: [
        "Beneficiary identity behind hot wallet not confirmed",
      ],
      labels: [
        { source: "community_tagset", freshness: "2025-10-15 (stale)", confidence_tier: "Medium" },
      ],
      path_directness_score: 0.71,
      corroboration_score: 0.58,
    },
  },
  graph: {
    case_id: "CASE-2026-0417",
    nodes: [
      { id: "n_vic", address: "bc1qvictim...origin", chain: "BTC", kind: "wallet", label: "Victim Wallet", is_terminal: false, amount: 4.2 },
      { id: "n_hop1", address: "bc1qhop1...peel1", chain: "BTC", kind: "wallet", label: "Hop 1 · 2h", is_terminal: false, amount: 4.07 },
      { id: "n_hop3", address: "bc1qhop3...peel2", chain: "BTC", kind: "wallet", label: "Hop 3 · peel", is_terminal: false, amount: 3.92 },
      { id: "n_unres", address: "bc1qunresolved...cold", chain: "BTC", kind: "wallet", label: "Unresolved Branch", evidence_tier: "Unknown", is_terminal: true, amount: 0.15 },
      { id: "n_hop5", address: "bc1qhop5...layer", chain: "BTC", kind: "wallet", label: "Hop 5", is_terminal: false, amount: 3.75 },
      { id: "n_bridge", address: "0xbridge...contract", chain: "BTC", kind: "bridge_contract", label: "Bridge Leg", is_terminal: false, amount: 3.70 },
      { id: "n_vasp", address: "0xvaspx...custody", chain: "ETH", kind: "vasp", label: "VASP-X Hot Wallet", evidence_tier: "Medium", is_terminal: true, amount: 3.65 },
    ],
    edges: [
      { id: "e1", source: "n_vic", target: "n_hop1", type: "TRANSACTION", amount: 4.2, asset: "BTC", timestamp: "2026-09-08T08:00:00Z", hop_index: 0, value_retained_pct: 0.97 },
      { id: "e2", source: "n_hop1", target: "n_hop3", type: "TRANSACTION", amount: 4.07, asset: "BTC", timestamp: "2026-09-08T10:15:00Z", hop_index: 1, value_retained_pct: 0.96 },
      { id: "e3_unres", source: "n_hop3", target: "n_unres", type: "TRANSACTION", amount: 0.15, asset: "BTC", timestamp: "2026-09-08T11:00:00Z", hop_index: 2, value_retained_pct: 0.04 },
      { id: "e3", source: "n_hop3", target: "n_hop5", type: "TRANSACTION", amount: 3.77, asset: "BTC", timestamp: "2026-09-08T11:20:00Z", hop_index: 2, value_retained_pct: 0.96 },
      { id: "e4", source: "n_hop5", target: "n_bridge", type: "TRANSACTION", amount: 3.70, asset: "BTC", timestamp: "2026-09-08T14:40:00Z", hop_index: 3, value_retained_pct: 0.98 },
      { id: "e5", source: "n_bridge", target: "n_vasp", type: "CROSS_CHAIN_LINK", amount: 3.65, asset: "WBTC", timestamp: "2026-09-08T16:00:00Z", hop_index: 4, cross_chain_confidence: 0.62, bridge_contract: "0xbridge...contract", asset_mapping: "BTC -> WBTC" },
    ],
    termination_reason: "known_service_boundary",
  },
  attribution: {
    case_id: "CASE-2026-0417",
    candidates: [
      {
        candidate_id: "cand-s2-01",
        vasp_name: "VASP-X (exchange, verified)",
        branch_id: "branch-1",
        evidence_tier: "Medium",
        supporting_evidence: [
          "Single crowdsourced label, clean 2-hop path",
          "Consistent deposit/withdrawal service pattern",
          "Value retention $>90\\%$ across hops",
        ],
        contradicting_evidence: [
          "VASP-X label verified 340 days ago; community flags dormancy",
        ],
        unknowns: [
          "Beneficiary KYC identity not confirmed",
        ],
        labels: [
          { source: "community_tagset", freshness: "2025-10-15 (stale)", confidence_tier: "Medium" },
        ],
        path_directness_score: 0.71,
        corroboration_score: 0.58,
      },
      {
        candidate_id: "cand-s2-02",
        vasp_name: "Unnamed hot wallet cluster",
        branch_id: "branch-2",
        evidence_tier: "Weak",
        supporting_evidence: ["Cluster heuristic linked to Asian OTC desk"],
        contradicting_evidence: ["High hop count (7 hops), low timing correlation"],
        unknowns: ["Unregistered operator"],
        labels: [{ source: "cluster_heuristic", freshness: "2026-01-01", confidence_tier: "Weak" }],
        path_directness_score: 0.44,
        corroboration_score: 0.22,
      },
      {
        candidate_id: "cand-s2-03",
        vasp_name: null,
        branch_id: "branch-3",
        evidence_tier: "Unknown",
        supporting_evidence: [],
        contradicting_evidence: [],
        unknowns: ["Terminal address on this peel branch carries zero labels"],
        labels: [],
        path_directness_score: 0.32,
        corroboration_score: 0.0,
      },
    ],
    patterns: [
      {
        pattern: "peel_chain",
        label: "Peel chain",
        explanation: "Branch-1 shows small amounts peeled off at each hop while bulk value advances.",
        branch_id: "branch-1",
      },
      {
        pattern: "structuring",
        label: "Structuring (flag only)",
        explanation: "Multiple transfers sit just under ₹50,000 threshold. Flagged for review; not a proof of crime.",
        branch_id: "branch-1",
      },
      {
        pattern: "bridge_detected",
        label: "Cross-chain bridge",
        explanation: "Hop 5 correlated across BTC -> ETH bridge with 62% confidence.",
        branch_id: "branch-1",
      },
    ],
    metrics: {
      rule_risk_score: 0.72,
      attribution_confidence: 0.65,
      ml_probability: 0.78,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "mixer_proximity_score", importance: 0.54 },
          { feature: "repeating_peel_ratio", importance: 0.28 },
          { feature: "structuring_frequency", importance: 0.12 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
  },
  atlas: {
    case_id: "CASE-2026-0417",
    alternatives: [
      {
        hypothesis: "Funds may have passed through an intermediary wallet with unrelated ownership before reaching VASP-X.",
        plausibility: 0.38,
      },
      {
        hypothesis: "Terminal address belongs to an unlisted OTC desk sharing hot wallet infrastructure.",
        plausibility: 0.24,
      },
    ],
    contradictions: [
      "VASP-X's label was last verified 340 days ago; a more recent community report flags address as inactive.",
      "Timing gap of 6 hours between hop 3 and hop 5 is longer than standard automated custodial sweeps.",
    ],
    missing_data: [
      "No independent confirmation exists for the bridge leg beyond timing and amount correlation.",
      "Request bridge contract event logs directly from target chain indexer.",
    ],
    robustness_score: 0.58, // Fragile state!
  },
  evidence: [
    { record_id: "rec-0001", case_id: "CASE-2026-0417", record_type: "case_created", content_hash: "3f9a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", previous_hash: "GENESIS", created_at: "2026-09-11T09:12:00Z", status: "PASS" },
    { record_id: "rec-0002", case_id: "CASE-2026-0417", record_type: "trace_step", content_hash: "8b2e5d9a4c1f7036e2d8b4a19c5f7e3021b4d6f8a9c1e3057192b3d4e5f60718", previous_hash: "3f9a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", created_at: "2026-09-11T09:14:22Z", status: "PASS" },
    { record_id: "rec-0003", case_id: "CASE-2026-0417", record_type: "attribution", content_hash: "c4a7f1e8093b5d2a6f4c8b1e9d3a705f2c4e6b8a91d3f5709182b3c4d5e6f708", previous_hash: "8b2e5d9a4c1f7036e2d8b4a19c5f7e3021b4d6f8a9c1e3057192b3d4e5f60718", created_at: "2026-09-11T09:22:47Z", status: "PASS" },
    { record_id: "rec-0004", case_id: "CASE-2026-0417", record_type: "atlas_challenge", content_hash: "1d6f9b3e7a2c5081d4f6a9c2e5b8073f1d4a6c9e2b5f8071d3a6c9f2e5b8071d", previous_hash: "c4a7f1e8093b5d2a6f4c8b1e9d3a705f2c4e6b8a91d3f5709182b3c4d5e6f708", created_at: "2026-09-11T09:31:05Z", status: "PASS" },
    { record_id: "rec-0005", case_id: "CASE-2026-0417", record_type: "external_callback", content_hash: "e2b5c8f1a4d7902b5e8c1f4a7d0b3e6c9f2a5d8b1e4c7f0a3d6b9e2c5f8a1d4b", previous_hash: "1d6f9b3e7a2c5081d4f6a9c2e5b8073f1d4a6c9e2b5f8071d3a6c9f2e5b8071d", created_at: "2026-09-11T09:40:11Z", status: "PASS", is_simulated: true },
  ],
  recommendation: {
    rec_id: "rec-s2-act-01",
    case_id: "CASE-2026-0417",
    finding: "3.65 WBTC traced to VASP-X custodial address following peel chain layering.",
    target_vasp: "VASP-X Global Legal Compliance",
    target_address: "0xvaspx...custody",
    suggested_action: "freeze_notice",
    action_title: "Issue VASP Freeze & Subpoena Notice",
    statutory_basis: "Section 91 CrPC r/w IT Act 2000 (Simulated NCRP/SAHYOG)",
    confidence: 0.65,
    approval_status: "pending",
  },
};

// ---------------------------------------------------------------------------
// 3. Scenario 3: Cross-Chain Bridge Correlation (BTC to ETH)
// ---------------------------------------------------------------------------
const scenario3: ScenarioBundle = {
  summary: {
    case_id: "CASE-2026-0398",
    scenario_id: "scenario_3_cross_chain",
    status: "in_review",
    created_at: "2026-09-12T04:00:00Z",
    reported_at_display: "2 days ago",
    amount_inr: "₹8,50,000",
    crypto_amount: "1.0 BTC -> 15.2 ETH",
    complaint_ref: "NCRP complaint #77319",
    pattern_summary: "Lock/burn bridge hop with timing/amount correlation",
    metrics: {
      rule_risk_score: 0.68,
      attribution_confidence: 0.58,
      ml_probability: 0.64,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "cross_chain_volume_ratio", importance: 0.62 },
          { feature: "bridge_delay_score", importance: 0.24 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
    leading_candidate: {
      candidate_id: "cand-s3-01",
      vasp_name: "Binance Bridge Recipient Hot Wallet",
      branch_id: "branch-cross",
      evidence_tier: "Medium",
      supporting_evidence: [
        "Lock tx on BTC matches Mint tx on ETH within 120s timing tolerance",
        "Net asset correlation BTC to WBTC exact after 0.05% fee deduction",
      ],
      contradicting_evidence: [],
      unknowns: [
        "Cross-chain bridge links carry explicit lower confidence by protocol rule",
      ],
      labels: [
        { source: "bridge_oracle_registry", freshness: "2026-09-12", confidence_tier: "Medium" },
      ],
      path_directness_score: 0.65,
      corroboration_score: 0.60,
    },
  },
  graph: {
    case_id: "CASE-2026-0398",
    nodes: [
      { id: "s3_btc_victim", address: "bc1q...btc_vic", chain: "BTC", kind: "wallet", label: "BTC Victim", is_terminal: false, amount: 1.0 },
      { id: "s3_btc_lock", address: "bc1q...portal", chain: "BTC", kind: "bridge_contract", label: "Portal Lock Custody", is_terminal: false, amount: 1.0 },
      { id: "s3_eth_mint", address: "0xbridge...minter", chain: "ETH", kind: "bridge_contract", label: "Bridge Minter", is_terminal: false, amount: 15.2 },
      { id: "s3_eth_vasp", address: "0xbinance...deposit", chain: "ETH", kind: "vasp", label: "Binance ETH Deposit", evidence_tier: "Medium", is_terminal: true, amount: 15.18 },
    ],
    edges: [
      { id: "s3_e1", source: "s3_btc_victim", target: "s3_btc_lock", type: "TRANSACTION", amount: 1.0, asset: "BTC", timestamp: "2026-09-12T04:10:00Z", hop_index: 0 },
      { id: "s3_e2", source: "s3_btc_lock", target: "s3_eth_mint", type: "CROSS_CHAIN_LINK", amount: 15.2, asset: "ETH", timestamp: "2026-09-12T04:12:00Z", hop_index: 1, cross_chain_confidence: 0.65, bridge_contract: "PortalBridge", asset_mapping: "BTC -> WETH" },
      { id: "s3_e3", source: "s3_eth_mint", target: "s3_eth_vasp", type: "TRANSACTION", amount: 15.18, asset: "ETH", timestamp: "2026-09-12T04:45:00Z", hop_index: 2 },
    ],
    termination_reason: "known_service_boundary",
  },
  attribution: {
    case_id: "CASE-2026-0398",
    candidates: [
      {
        candidate_id: "cand-s3-01",
        vasp_name: "Binance Bridge Recipient Hot Wallet",
        branch_id: "branch-cross",
        evidence_tier: "Medium",
        supporting_evidence: [
          "Lock tx on BTC matches Mint tx on ETH within 120s timing tolerance",
          "Net asset correlation BTC to WBTC exact after 0.05% fee deduction",
        ],
        contradicting_evidence: [],
        unknowns: [
          "Cross-chain bridge links carry explicit lower confidence by protocol rule",
        ],
        labels: [
          { source: "bridge_oracle_registry", freshness: "2026-09-12", confidence_tier: "Medium" },
        ],
        path_directness_score: 0.65,
        corroboration_score: 0.60,
      },
    ],
    patterns: [
      {
        pattern: "bridge_detected",
        label: "Bridge Correlated",
        explanation: "Lock on BTC correlated with Mint on ETH. Explicit uncertainty applied (65%).",
        branch_id: "branch-cross",
      },
    ],
    metrics: {
      rule_risk_score: 0.68,
      attribution_confidence: 0.58,
      ml_probability: 0.64,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "cross_chain_volume_ratio", importance: 0.62 },
          { feature: "bridge_delay_score", importance: 0.24 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
  },
  atlas: {
    case_id: "CASE-2026-0398",
    alternatives: [
      { hypothesis: "Bridge mint event was initiated by an unrelated parallel swap transaction.", plausibility: 0.35 },
    ],
    contradictions: [],
    missing_data: ["Request lock tx payload cryptographic signature verification from bridge validators."],
    robustness_score: 0.65,
  },
  evidence: [
    { record_id: "rec-s3-001", case_id: "CASE-2026-0398", record_type: "case_created", content_hash: "333a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", previous_hash: "GENESIS", created_at: "2026-09-12T04:00:00Z", status: "PASS" },
    { record_id: "rec-s3-002", case_id: "CASE-2026-0398", record_type: "cross_chain_correlation", content_hash: "444e5d9a4c1f7036e2d8b4a19c5f7e3021b4d6f8a9c1e3057192b3d4e5f60718", previous_hash: "333a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", created_at: "2026-09-12T04:15:00Z", status: "PASS" },
  ],
  recommendation: {
    rec_id: "rec-s3-act-01",
    case_id: "CASE-2026-0398",
    finding: "15.18 ETH destination deposit correlated from BTC lock event via PortalBridge.",
    target_vasp: "Binance Compliance (India Desk)",
    target_address: "0xbinance...deposit",
    suggested_action: "freeze_notice",
    action_title: "Cross-Chain Deposit Freeze Request",
    statutory_basis: "Section 91 CrPC",
    confidence: 0.58,
    approval_status: "pending",
  },
};

// ---------------------------------------------------------------------------
// 4. Scenario 4: Mixer Boundary (Wasabi / Tornado Cash)
// ---------------------------------------------------------------------------
const scenario4: ScenarioBundle = {
  summary: {
    case_id: "CASE-2026-0403",
    scenario_id: "scenario_4_mixer",
    status: "open",
    created_at: "2026-09-13T01:10:00Z",
    reported_at_display: "1 day ago",
    amount_inr: "₹6,10,000",
    crypto_amount: "5.0 ETH",
    complaint_ref: "NCRP complaint #66501",
    pattern_summary: "Mixer privacy boundary hit · evidentiary break",
    metrics: {
      rule_risk_score: 0.95,
      attribution_confidence: 0.10, // Very low attribution confidence due to mixer break!
      ml_probability: 0.96,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "mixer_contract_deposit_flag", importance: 0.89 },
          { feature: "high_fanout_anonymity_pool", importance: 0.08 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
    leading_candidate: {
      candidate_id: "cand-s4-01",
      vasp_name: null,
      branch_id: "branch-mixer",
      evidence_tier: "Unknown",
      supporting_evidence: [],
      contradicting_evidence: ["Evidentiary break: funds entered privacy pool; deterministic trace terminated"],
      unknowns: [
        "Cryptographic anonymity pool breaks transaction graph linkability",
        "Withdrawal address cannot be mathematically proven on public explorer data",
      ],
      labels: [],
      path_directness_score: 0.1,
      corroboration_score: 0.0,
    },
  },
  graph: {
    case_id: "CASE-2026-0403",
    nodes: [
      { id: "s4_victim", address: "0xvictim...s4", chain: "ETH", kind: "wallet", label: "Victim Wallet", is_terminal: false, amount: 5.0 },
      { id: "s4_hop1", address: "0xforwarder...s4", chain: "ETH", kind: "wallet", label: "Forwarder", is_terminal: false, amount: 4.98 },
      { id: "s4_mixer", address: "0x08b8...TornadoContract", chain: "ETH", kind: "mixer", label: "Tornado Cash Pool (Evidentiary Break)", evidence_tier: "Unknown", is_terminal: true, amount: 4.95 },
    ],
    edges: [
      { id: "s4_e1", source: "s4_victim", target: "s4_hop1", type: "TRANSACTION", amount: 5.0, asset: "ETH", timestamp: "2026-09-13T01:15:00Z", hop_index: 0 },
      { id: "s4_e2", source: "s4_hop1", target: "s4_mixer", type: "TRANSACTION", amount: 4.95, asset: "ETH", timestamp: "2026-09-13T01:45:00Z", hop_index: 1 },
    ],
    termination_reason: "evidentiary_break",
  },
  attribution: {
    case_id: "CASE-2026-0403",
    candidates: [
      {
        candidate_id: "cand-s4-01",
        vasp_name: null,
        branch_id: "branch-mixer",
        evidence_tier: "Unknown",
        supporting_evidence: [],
        contradicting_evidence: ["Evidentiary break: funds entered privacy pool; deterministic trace terminated"],
        unknowns: [
          "Cryptographic anonymity pool breaks transaction graph linkability",
          "Withdrawal address cannot be mathematically proven on public explorer data",
        ],
        labels: [],
        path_directness_score: 0.1,
        corroboration_score: 0.0,
      },
    ],
    patterns: [
      {
        pattern: "mixer_privacy_boundary",
        label: "Mixer Boundary Hit",
        explanation: "Hop 2 deposited directly into Tornado Cash privacy pool. Trace halted per evidentiary limits.",
        branch_id: "branch-mixer",
      },
    ],
    metrics: {
      rule_risk_score: 0.95,
      attribution_confidence: 0.10,
      ml_probability: 0.96,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "mixer_contract_deposit_flag", importance: 0.89 },
          { feature: "high_fanout_anonymity_pool", importance: 0.08 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
  },
  atlas: {
    case_id: "CASE-2026-0403",
    alternatives: [],
    contradictions: ["Deterministic graph linkability ceases at anonymity contract boundary."],
    missing_data: ["Off-chain intelligence / relayer IP logs required to associate pool withdrawal."],
    robustness_score: 0.20,
  },
  evidence: [
    { record_id: "rec-s4-001", case_id: "CASE-2026-0403", record_type: "case_created", content_hash: "555a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", previous_hash: "GENESIS", created_at: "2026-09-13T01:10:00Z", status: "PASS" },
    { record_id: "rec-s4-002", case_id: "CASE-2026-0403", record_type: "mixer_boundary_termination", content_hash: "666e5d9a4c1f7036e2d8b4a19c5f7e3021b4d6f8a9c1e3057192b3d4e5f60718", previous_hash: "555a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", created_at: "2026-09-13T01:50:00Z", status: "PASS" },
  ],
  recommendation: {
    rec_id: "rec-s4-act-01",
    case_id: "CASE-2026-0403",
    finding: "Trace terminated at Tornado Cash mixer contract 0x08b8. Evidentiary break.",
    target_vasp: "Indian Cyber Crime Coordination Centre (I4C)",
    target_address: "0x08b8...TornadoContract",
    suggested_action: "close_unresolved",
    action_title: "Escalate to Off-Chain Relayer Subpoena Unit",
    statutory_basis: "Advisory note: public tracing boundary reached",
    confidence: 0.10,
    approval_status: "pending",
  },
};

// ---------------------------------------------------------------------------
// 5. Scenario 5: Conflicting Labels (Regional OTC vs Exchange)
// ---------------------------------------------------------------------------
const scenario5: ScenarioBundle = {
  summary: {
    case_id: "CASE-2026-0411",
    scenario_id: "scenario_5_conflicting",
    status: "in_review",
    created_at: "2026-09-13T10:00:00Z",
    reported_at_display: "1 day ago",
    amount_inr: "₹3,40,000",
    crypto_amount: "1.8 BTC",
    complaint_ref: "NCRP complaint #55120",
    pattern_summary: "Conflicting source labels · Weak attribution tier",
    metrics: {
      rule_risk_score: 0.55,
      attribution_confidence: 0.38,
      ml_probability: 0.45,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "label_provenance_conflict_index", importance: 0.74 },
          { feature: "cluster_entropy", importance: 0.18 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
    leading_candidate: {
      candidate_id: "cand-s5-01",
      vasp_name: "Regional OTC Desk (disputed)",
      branch_id: "branch-conflicting",
      evidence_tier: "Weak",
      supporting_evidence: [
        "Source A tags address as cold-storage sweep for a major exchange",
      ],
      contradicting_evidence: [
        "Source B (equally fresh) tags same address as unrelated unregulated OTC desk",
        "Corroboration score collapsed due to active contradictory tags",
      ],
      unknowns: [
        "True entity identity cannot be resolved without proprietary KYC records",
      ],
      labels: [
        { source: "chain_partner_alpha", freshness: "2026-09-02", confidence_tier: "Medium" },
        { source: "chain_partner_beta", freshness: "2026-09-05", confidence_tier: "Medium" },
      ],
      path_directness_score: 0.48,
      corroboration_score: 0.20,
    },
  },
  graph: {
    case_id: "CASE-2026-0411",
    nodes: [
      { id: "s5_vic", address: "bc1qvictim...s5", chain: "BTC", kind: "wallet", label: "Victim Wallet", is_terminal: false, amount: 1.8 },
      { id: "s5_hop", address: "bc1qrelay...s5", chain: "BTC", kind: "wallet", label: "Relay Node", is_terminal: false, amount: 1.78 },
      { id: "s5_cand", address: "bc1qdisputed...s5", chain: "BTC", kind: "vasp", label: "Disputed OTC/Exchange Wallet", evidence_tier: "Weak", is_terminal: true, amount: 1.75 },
    ],
    edges: [
      { id: "s5_e1", source: "s5_vic", target: "s5_hop", type: "TRANSACTION", amount: 1.8, asset: "BTC", timestamp: "2026-09-13T10:10:00Z", hop_index: 0 },
      { id: "s5_e2", source: "s5_hop", target: "s5_cand", type: "TRANSACTION", amount: 1.75, asset: "BTC", timestamp: "2026-09-13T11:20:00Z", hop_index: 1 },
    ],
    termination_reason: "known_service_boundary",
  },
  attribution: {
    case_id: "CASE-2026-0411",
    candidates: [
      {
        candidate_id: "cand-s5-01",
        vasp_name: "Regional OTC Desk (disputed)",
        branch_id: "branch-conflicting",
        evidence_tier: "Weak",
        supporting_evidence: [
          "Source A tags address as cold-storage sweep for a major exchange",
        ],
        contradicting_evidence: [
          "Source B (equally fresh) tags same address as unrelated unregulated OTC desk",
          "Corroboration score collapsed due to active contradictory tags",
        ],
        unknowns: [
          "True entity identity cannot be resolved without proprietary KYC records",
        ],
        labels: [
          { source: "chain_partner_alpha", freshness: "2026-09-02", confidence_tier: "Medium" },
          { source: "chain_partner_beta", freshness: "2026-09-05", confidence_tier: "Medium" },
        ],
        path_directness_score: 0.48,
        corroboration_score: 0.20,
      },
    ],
    patterns: [
      {
        pattern: "peel_chain",
        label: "Peel Chain",
        explanation: "Minor amounts peeled off during transit.",
        branch_id: "branch-conflicting",
      },
    ],
    metrics: {
      rule_risk_score: 0.55,
      attribution_confidence: 0.38,
      ml_probability: 0.45,
      ml: {
        output_label: "model_output",
        is_model_output: true,
        model_name: "risk_scoring_xgb_gpu",
        model_version: "risk_xgb_gpu-2026.09.10-1",
        device: "cuda",
        top_features: [
          { feature: "label_provenance_conflict_index", importance: 0.74 },
          { feature: "cluster_entropy", importance: 0.18 },
        ],
        disclaimer: "Statistical prioritization signal only. Does not decide VASP attribution or prove facts.",
      },
    },
  },
  atlas: {
    case_id: "CASE-2026-0411",
    alternatives: [
      { hypothesis: "Address is a non-custodial high-net-worth wallet rather than an OTC entity.", plausibility: 0.48 },
    ],
    contradictions: [
      "Partner Alpha labels address as tier-1 exchange; Partner Beta explicitly disputes and labels as OTC desk.",
    ],
    missing_data: ["Request verified label confirmation from FIU-IND provenance feed."],
    robustness_score: 0.38,
  },
  evidence: [
    { record_id: "rec-s5-001", case_id: "CASE-2026-0411", record_type: "case_created", content_hash: "777a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", previous_hash: "GENESIS", created_at: "2026-09-13T10:00:00Z", status: "PASS" },
    { record_id: "rec-s5-002", case_id: "CASE-2026-0411", record_type: "label_conflict_detected", content_hash: "888e5d9a4c1f7036e2d8b4a19c5f7e3021b4d6f8a9c1e3057192b3d4e5f60718", previous_hash: "777a1c7e2b8d4560f1a2b3c4d5e6f7089a1b2c3d4e5f60718293a4b5c6d7e8f9", created_at: "2026-09-13T10:15:00Z", status: "PASS" },
  ],
  recommendation: {
    rec_id: "rec-s5-act-01",
    case_id: "CASE-2026-0411",
    finding: "Address bc1qdisputed carries conflicting labels between exchange custody and OTC desk.",
    target_vasp: "Both Potential Custodians",
    target_address: "bc1qdisputed...s5",
    suggested_action: "kyc_request",
    action_title: "Dual Information Subpoena (Section 91 CrPC)",
    statutory_basis: "Investigatory notice to resolve conflicting ownership",
    confidence: 0.38,
    approval_status: "pending",
  },
};

export const ALL_SCENARIOS: Record<string, ScenarioBundle> = {
  "CASE-2026-0417": scenario2, // Primary reference case
  "case-demo-001": scenario2,  // Alias for backward compatibility
  "CASE-2026-0001": scenario1,
  "scenario_1_direct": scenario1,
  "CASE-2026-0398": scenario3,
  "scenario_3_cross_chain": scenario3,
  "CASE-2026-0403": scenario4,
  "scenario_4_mixer": scenario4,
  "CASE-2026-0411": scenario5,
  "scenario_5_conflicting": scenario5,
};

export const QUEUE_CASES: QueueCaseItem[] = [
  {
    case_id: "CASE-2026-0417",
    scenario_id: "scenario_2_peel",
    name: "Peel Chain Layering",
    chain: "BTC",
    status: "in_review",
    tier_dot: "Medium",
    fraud_category: "Investment Fraud",
    amount_inr: "₹4,20,000",
    crypto_amount: "4.2 BTC",
    pattern_type: "Peel chain · Structuring",
    reported_ago: "3 days ago",
    complaint_id: "NCRP-88213",
  },
  {
    case_id: "CASE-2026-0001",
    scenario_id: "scenario_1_direct",
    name: "Direct VASP Sweep",
    chain: "ETH",
    status: "open",
    tier_dot: "Strong",
    fraud_category: "Phishing / Drainer",
    amount_inr: "₹2,10,000",
    crypto_amount: "2.5 ETH",
    pattern_type: "Direct VASP deposit",
    reported_ago: "1 day ago",
    complaint_id: "NCRP-91024",
  },
  {
    case_id: "CASE-2026-0411",
    scenario_id: "scenario_5_conflicting",
    name: "Conflicting VASP Labels",
    chain: "BTC",
    status: "in_review",
    tier_dot: "Weak",
    fraud_category: "Task Scam / OTC",
    amount_inr: "₹3,40,000",
    crypto_amount: "1.8 BTC",
    pattern_type: "Disputed OTC entity",
    reported_ago: "1 day ago",
    complaint_id: "NCRP-55120",
  },
  {
    case_id: "CASE-2026-0403",
    scenario_id: "scenario_4_mixer",
    name: "Tornado Mixer Boundary",
    chain: "ETH",
    status: "open",
    tier_dot: "Unknown",
    fraud_category: "Ransomware Extortion",
    amount_inr: "₹6,10,000",
    crypto_amount: "5.0 ETH",
    pattern_type: "Mixer privacy boundary",
    reported_ago: "1 day ago",
    complaint_id: "NCRP-66501",
  },
  {
    case_id: "CASE-2026-0398",
    scenario_id: "scenario_3_cross_chain",
    name: "Cross-Chain Portal Bridge",
    chain: "BTC",
    status: "in_review",
    tier_dot: "Medium",
    fraud_category: "Crypto Staking Scam",
    amount_inr: "₹8,50,000",
    crypto_amount: "1.0 BTC -> 15.2 ETH",
    pattern_type: "Cross-chain bridge",
    reported_ago: "2 days ago",
    complaint_id: "NCRP-77319",
  },
];

export function getScenario(caseId: string): ScenarioBundle {
  return ALL_SCENARIOS[caseId] ?? scenario2;
}
