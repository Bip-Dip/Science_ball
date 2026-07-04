import { post } from './client';

export interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, any>;
}

export interface GraphEdge {
  source_id: string;
  target_id: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphNeighborhood {
  center_node_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface NeighborhoodRequest {
  node_id: string;
  label: string;
  depth?: number;
}

export const graphApi = {
  async getNeighborhood(request: NeighborhoodRequest): Promise<GraphNeighborhood> {
    return post<GraphNeighborhood>('/api/v1/graph/neighborhood', request);
  },
};
