"use client";

import { useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  MarkerType,
  type Node,
  type Edge,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Wallet, Landmark, Shuffle, Link2, Flag } from "lucide-react";
import type { GraphData, TraceNode, TraceEdge, NodeKind, EvidenceTier } from "@/lib/api/types";
import PathDetail from "./PathDetail";

interface GraphViewProps {
  graphData: GraphData;
  compact?: boolean;
}

type KindStyle = {
  icon: typeof Wallet;
  border: string;
  bg: string;
  text: string;
  label: string;
};

const KIND_STYLES: Record<NodeKind, KindStyle> = {
  wallet: {
    icon: Wallet,
    border: "border-[#2B2B2E]",
    bg: "bg-[#141415]",
    text: "text-[#E7EAEE]",
    label: "Wallet",
  },
  vasp: {
    icon: Landmark,
    border: "border-[#3FBE8B]/60",
    bg: "bg-[#141415]",
    text: "text-[#3FBE8B]",
    label: "VASP Custody",
  },
  mixer: {
    icon: Shuffle,
    border: "border-[#D5636A]/60",
    bg: "bg-[#141415]",
    text: "text-[#D5636A]",
    label: "Mixer Boundary",
  },
  bridge_contract: {
    icon: Link2,
    border: "border-[#E3AE3E]/60",
    bg: "bg-[#141415]",
    text: "text-[#E3AE3E]",
    label: "Bridge Contract",
  },
};

const TIER_BADGES: Record<EvidenceTier, string> = {
  Strong: "bg-[rgba(63,190,139,0.12)] text-[#3FBE8B] border-[rgba(63,190,139,0.3)]",
  Medium: "bg-[rgba(227,174,62,0.12)] text-[#E3AE3E] border-[rgba(227,174,62,0.3)]",
  Weak: "bg-[rgba(197,106,75,0.12)] text-[#C56A4B] border-[rgba(197,106,75,0.3)]",
  Unknown: "bg-[rgba(92,102,117,0.15)] text-[#5C6675] border-[rgba(92,102,117,0.3)]",
};

type TraceNodeData = {
  node: TraceNode;
};

function TraceNodeComponent({ data }: NodeProps) {
  const { node } = data as unknown as TraceNodeData;
  const style = KIND_STYLES[node.kind] ?? KIND_STYLES.wallet;
  const Icon = style.icon;

  return (
    <div
      className={[
        "min-w-[190px] max-w-[220px] rounded-lg border px-3 py-2.5 shadow-xl transition-all hover:border-[#3B82F6]",
        style.border,
        style.bg,
      ].join(" ")}
    >
      <Handle type="target" position={Position.Left} className="!bg-[#5A6373] !w-2 !h-2" />
      <Handle type="source" position={Position.Right} className="!bg-[#5A6373] !w-2 !h-2" />

      <div className="flex items-center justify-between gap-1.5">
        <div className="flex items-center gap-1.5">
          <Icon className={`h-3.5 w-3.5 shrink-0 ${style.text}`} strokeWidth={2} />
          <span className={`text-[10.5px] font-semibold uppercase tracking-wider ${style.text}`}>
            {style.label}
          </span>
        </div>
        <span className="font-mono-vajra text-[9px] uppercase px-1 py-0.5 rounded bg-[#0A0A0B] text-[#8A93A3] border border-[#2B2B2E]">
          {node.chain}
        </span>
      </div>

      <p className="mt-1 font-mono-vajra text-xs text-[#E7EAEE] truncate" title={node.address}>
        {node.address}
      </p>

      {node.label && (
        <p className="mt-0.5 text-xs text-[#8A93A3] truncate font-medium" title={node.label}>
          {node.label}
        </p>
      )}

      <div className="mt-2 flex items-center justify-between gap-1">
        {node.is_terminal ? (
          <span className="inline-flex items-center gap-1 rounded border border-[#2B2B2E] bg-[#1B1B1D] px-1.5 py-0.5 text-[9.5px] font-medium text-[#8A93A3]">
            <Flag className="h-2.5 w-2.5" />
            Terminal
          </span>
        ) : (
          <span className="text-[10px] font-mono-vajra text-[#5A6373]">
            {node.amount ? `${node.amount} ${node.chain}` : "transit"}
          </span>
        )}

        {node.evidence_tier && (
          <span className={`rounded-full border px-2 py-0.2 text-[9.5px] font-medium ${TIER_BADGES[node.evidence_tier]}`}>
            {node.evidence_tier}
          </span>
        )}
      </div>
    </div>
  );
}

const nodeTypes = { traceNode: TraceNodeComponent };

const COLUMN_SPACING_X = 260;
const ROW_SPACING_Y = 130;

function computeLevels(nodes: TraceNode[], edges: TraceEdge[]): Map<string, number> {
  const levels = new Map<string, number>();
  nodes.forEach((n) => levels.set(n.id, 0));

  const sortedEdges = [...edges].sort((a, b) => a.hop_index - b.hop_index);
  sortedEdges.forEach((edge) => {
    const sourceLevel = levels.get(edge.source) ?? 0;
    const candidateLevel = sourceLevel + 1;
    const currentTargetLevel = levels.get(edge.target) ?? 0;
    if (candidateLevel > currentTargetLevel) {
      levels.set(edge.target, candidateLevel);
    }
  });

  return levels;
}

function buildFlowNodes(nodes: TraceNode[], levels: Map<string, number>): Node[] {
  const columnCounts = new Map<number, number>();

  return nodes.map((node) => {
    const level = levels.get(node.id) ?? 0;
    const rowIndex = columnCounts.get(level) ?? 0;
    columnCounts.set(level, rowIndex + 1);

    return {
      id: node.id,
      type: "traceNode",
      position: { x: level * COLUMN_SPACING_X + 40, y: rowIndex * ROW_SPACING_Y + 50 },
      data: { node } satisfies TraceNodeData,
    };
  });
}

function buildFlowEdges(edges: TraceEdge[]): Edge[] {
  return edges.map((edge) => {
    const isCrossChain = edge.type === "CROSS_CHAIN_LINK";

    if (isCrossChain) {
      const conf = Math.round((edge.cross_chain_confidence ?? 0.6) * 100);
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#E3AE3E",
          strokeWidth: 2.2,
          strokeDasharray: "6 4",
        },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#E3AE3E" },
        label: `⚠ cross-chain · ${conf}% conf`,
        labelStyle: { fill: "#E3AE3E", fontSize: 10, fontWeight: 600, fontFamily: "var(--font-ibm-plex-mono)" },
        labelBgStyle: { fill: "#141415", fillOpacity: 0.95 },
        labelBgPadding: [6, 3] as [number, number],
        labelBgBorderRadius: 4,
      } satisfies Edge;
    }

    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: "smoothstep",
      animated: false,
      style: {
        stroke: "#3B82F6",
        strokeWidth: 2,
      },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#3B82F6" },
      label: `${edge.amount} ${edge.asset}`,
      labelStyle: { fill: "#8A93A3", fontSize: 10, fontWeight: 500, fontFamily: "var(--font-ibm-plex-mono)" },
      labelBgStyle: { fill: "#141415", fillOpacity: 0.9 },
      labelBgPadding: [4, 2] as [number, number],
      labelBgBorderRadius: 3,
    } satisfies Edge;
  });
}

export default function GraphView({ graphData, compact = false }: GraphViewProps) {
  const [selectedNode, setSelectedNode] = useState<TraceNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<TraceEdge | null>(null);

  const { nodes: flowNodes, edges: flowEdges } = useMemo(() => {
    const levels = computeLevels(graphData.nodes, graphData.edges);
    return {
      nodes: buildFlowNodes(graphData.nodes, levels),
      edges: buildFlowEdges(graphData.edges),
    };
  }, [graphData]);

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    const traceNode = (node.data as unknown as TraceNodeData)?.node;
    if (traceNode) {
      setSelectedNode(traceNode);
      setSelectedEdge(null);
    }
  };

  const onEdgeClick = (_: React.MouseEvent, edge: Edge) => {
    const traceEdge = graphData.edges.find((e) => e.id === edge.id);
    if (traceEdge) {
      setSelectedEdge(traceEdge);
      setSelectedNode(null);
    }
  };

  if (!graphData.nodes || graphData.nodes.length === 0) {
    return (
      <div className="h-full w-full flex items-center justify-center rounded-lg border border-[#2B2B2E] bg-[#0A0A0B] p-6 text-center">
        <div className="space-y-1">
          <p className="text-sm font-medium text-[#E7EAEE]">No trace graph available</p>
          <p className="text-xs text-[#5A6373]">Backend is currently offline or no trace hops have been seeded for this case.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full relative rounded-lg border border-[#2B2B2E] bg-[#0A0A0B] overflow-hidden">
      {/* 0 Outbound Transactions / Unspent Banner */}
      {graphData.nodes.length === 1 && graphData.edges.length === 0 && (
        <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between gap-3 rounded-md border border-[#2B2B2E] bg-[#141415]/95 px-4 py-2.5 backdrop-blur-md shadow-lg">
          <div className="flex items-center gap-2.5">
            <span className="inline-block h-2 w-2 rounded-full bg-[#3B82F6]" />
            <span className="text-xs font-medium text-[#E7EAEE]">
              Origin Node: <span className="text-[#8A93A3]">0 outbound transactions detected on-chain. Funds have not moved from this wallet.</span>
            </span>
          </div>
          <span className="rounded bg-[#1B1B1D] px-2 py-0.5 text-[10px] uppercase font-mono tracking-wider text-[#8A93A3] border border-[#2B2B2E]">
            Authentic On-Chain Reality
          </span>
        </div>
      )}

      <ReactFlow
        key={graphData.case_id || "vajra-graph"}
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        fitView
        fitViewOptions={{ padding: compact ? 0.15 : 0.25 }}
        proOptions={{ hideAttribution: true }}
        minZoom={0.2}
        maxZoom={1.8}
      >
        <Background color="#1B1B1D" gap={18} size={1} />
        {!compact && (
          <Controls className="!border !border-[#2B2B2E] !bg-[#141415] [&>button]:!border-[#2B2B2E] [&>button]:!bg-[#141415] [&>button]:!fill-[#8A93A3] [&>button:hover]:!bg-[#1B1B1D]" />
        )}
        {!compact && (
          <MiniMap
            className="!border !border-[#2B2B2E] !bg-[#141415]"
            maskColor="rgba(10, 10, 11, 0.75)"
            nodeColor={(node) => {
              const kind = (node.data as unknown as TraceNodeData)?.node?.kind;
              switch (kind) {
                case "vasp":
                  return "#3FBE8B";
                case "mixer":
                  return "#D5636A";
                case "bridge_contract":
                  return "#E3AE3E";
                default:
                  return "#3B82F6";
              }
            }}
          />
        )}
      </ReactFlow>

      {/* Pop-out Inspector Drawer */}
      <PathDetail
        selectedNode={selectedNode}
        selectedEdge={selectedEdge}
        onClose={() => {
          setSelectedNode(null);
          setSelectedEdge(null);
        }}
      />

      {/* Legend Footer */}
      <div className="absolute bottom-0 left-0 right-0 z-20 flex flex-wrap items-center gap-5 border-t border-[#2B2B2E] bg-[#141415]/90 px-4 py-2 text-[11.5px] text-[#8A93A3] backdrop-blur-sm">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 bg-[#3B82F6]" />
          Same-chain hop
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 border-t-2 border-dashed border-[#E3AE3E]" />
          Cross-chain link (explicit uncertainty)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 bg-[#5C6675]" />
          Terminated / unresolved
        </span>
        <span className="ml-auto text-[11px] text-[#5A6373]">
          Click any node or hop line to inspect evidence
        </span>
      </div>
    </div>
  );
}
