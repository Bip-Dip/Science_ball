import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  useReactFlow
} from 'reactflow';
import 'reactflow/dist/style.css';
import { graphApi, GraphNode, GraphEdge } from '../../api/graph';
import { Search, Info, AlertCircle } from 'lucide-react';

const NODE_COLORS: Record<string, string> = {
  Material: '#3b82f6', // blue-500
  Process: '#10b981', // emerald-500
  Equipment: '#f59e0b', // amber-500
  Document: '#6366f1', // indigo-500
  Chunk: '#94a3b8',    // slate-400
  Node: '#64748b',      // slate-500
};

export default function GraphPage() {
  const { fitView } = useReactFlow();
  const [nodes, setNodes] = useNodesState([]);
  const [edges, setEdges] = useEdgesState([]);
  const [query, setQuery] = useState({ node_id: '', label: 'Material' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const fetchNeighborhood = useCallback(async () => {
    if (!query.node_id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await graphApi.getNeighborhood({
        node_id: query.node_id,
        label: query.label,
        depth: 1
      });

      const flowNodes: Node[] = data.nodes.map((n, idx) => ({
        id: n.id,
        data: { label: n.properties.name || n.id, color: NODE_COLORS[n.label] || NODE_COLORS.Node, raw: n },
        position: {
            x: 400 + 200 * Math.cos(2 * Math.PI * idx / data.nodes.length),
            y: 300 + 200 * Math.sin(2 * Math.PI * idx / data.nodes.length)
        },
        style: {
            backgroundColor: NODE_COLORS[n.label] || NODE_COLORS.Node,
            color: 'white',
            fontWeight: 'bold',
            borderRadius: '50%',
            width: 60,
            height: 60,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            textAlign: 'center'
        },
      }));

      const flowEdges: Edge[] = data.edges.map((e, idx) => ({
        id: `e${idx}`,
        source: e.source_id,
        target: e.target_id,
        label: e.type,
        animated: true,
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
      setTimeout(() => fitView(), 100);
    } catch (err) {
      setError('Failed to fetch graph neighborhood.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [query, fitView]);

  const onNodeClick = (_: any, node: Node) => {
    setSelectedNode((node.data as any).raw);
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <div className="w-80 bg-white border-r border-slate-200 p-6 flex flex-col gap-6 shadow-sm z-10">
        <div>
          <h1 className="text-xl font-bold text-slate-800 mb-4">Knowledge Graph</h1>
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Node ID</label>
              <input
                type="text"
                value={query.node_id}
                onChange={(e) => setQuery({ ...query, node_id: e.target.value })}
                className="px-3 py-2 border border-slate-300 rounded-md text-sm outline-none"
                placeholder="e.g. nickel"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Label</label>
              <select
                value={query.label}
                onChange={(e) => setQuery({ ...query, label: e.target.value })}
                className="px-3 py-2 border border-slate-300 rounded-md text-sm bg-white outline-none"
              >
                <option value="Material">Material</option>
                <option value="Process">Process</option>
                <option value="Equipment">Equipment</option>
                <option value="Document">Document</option>
                <option value="Chunk">Chunk</option>
              </select>
            </div>
            <button
              onClick={fetchNeighborhood}
              disabled={loading || !query.node_id}
              className="mt-2 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:bg-slate-300 transition-colors"
            >
              {loading ? 'Loading...' : <><Search size={16} /> Explore</>}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-xs flex gap-2 items-start">
            <AlertCircle size={14} /> {error}
          </div>
        )}

        <div className="flex-1 overflow-y-auto">
          {selectedNode ? (
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-sm">
              <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
                <Info size={16} className="text-blue-500" /> Details
              </h3>
              <div className="space-y-3">
                <div>
                  <span className="block text-[10px] uppercase font-bold text-slate-400">ID</span>
                  <p className="text-slate-700 font-mono text-xs">{selectedNode.id}</p>
                </div>
                <div>
                  <span className="block text-[10px] uppercase font-bold text-slate-400">Label</span>
                  <p className="text-slate-800 font-medium">{selectedNode.label}</p>
                </div>
                <div>
                  <span className="block text-[10px] uppercase font-bold text-slate-400">Properties</span>
                  <pre className="bg-white p-2 rounded border border-slate-200 font-mono text-[11px] overflow-x-auto">
                    {JSON.stringify(selectedNode.properties, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-400 text-xs italic">Select a node for details</div>
          )}
        </div>
      </div>

      <div className="flex-1 relative bg-white">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={onNodeClick}
          connectionMode={ConnectionMode.Loose}
          fitView
        >
          <Background color="#cbd5e1" gap={20} />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
