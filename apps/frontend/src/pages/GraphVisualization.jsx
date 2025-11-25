import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ForceGraph2D from 'react-force-graph-2d';
import api from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { Loader2, ArrowLeft, Network, ZoomIn, ZoomOut, Play, Pause } from "lucide-react";

export default function GraphVisualization() {
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [limit, setLimit] = useState(2000);
    const [stats, setStats] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [highlightNodes, setHighlightNodes] = useState(new Set());
    const [highlightLinks, setHighlightLinks] = useState(new Set());
    const [isPaused, setIsPaused] = useState(false);
    const navigate = useNavigate();
    const { toast } = useToast();
    const fgRef = useRef();

    useEffect(() => {
        fetchGraphData();
    }, [limit]);

    useEffect(() => {
        if (graphData.nodes.length > 0 && fgRef.current) {
            setTimeout(() => {
                if (fgRef.current) {
                    fgRef.current.zoomToFit(400, 50);
                }
            }, 500);
        }
    }, [graphData]);

    const fetchGraphData = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/graph/knowledge-graph?limit=${limit}`);
            setGraphData(response.data);
            setStats(response.data.stats);
            toast({
                title: "✓ Graph loaded successfully",
                description: `Loaded ${response.data.stats.total_nodes} nodes and ${response.data.stats.total_links} links`,
                className: "bg-green-50 border-green-200 text-green-900",
            });
        } catch (error) {
            toast({
                title: "✗ Error loading graph",
                description: error.response?.data?.detail || error.message,
                className: "bg-red-50 border-red-200 text-red-900",
            });
        } finally {
            setLoading(false);
        }
    };

    const handleNodeClick = (node) => {
        const neighbors = new Set();
        const links = new Set();

        graphData.links.forEach(link => {
            if (link.source.id === node.id || link.source === node.id) {
                neighbors.add(link.target.id || link.target);
                links.add(link);
            }
            if (link.target.id === node.id || link.target === node.id) {
                neighbors.add(link.source.id || link.source);
                links.add(link);
            }
        });

        neighbors.add(node.id);
        setHighlightNodes(neighbors);
        setHighlightLinks(links);
    };

    const handleBackgroundClick = () => {
        setHighlightNodes(new Set());
        setHighlightLinks(new Set());
    };

    const getNodeColor = (node) => {
        if (highlightNodes.size > 0 && !highlightNodes.has(node.id)) {
            return 'rgba(100, 100, 100, 0.2)';
        }

        switch (node.type) {
            case 'item':
                return '#3b82f6';
            case 'topic':
                return '#10b981';
            case 'level':
                return '#f59e0b';
            default:
                return '#6b7280';
        }
    };

    const getNodeSize = (node) => {
        const connections = graphData.links.filter(link =>
            (link.source.id || link.source) === node.id ||
            (link.target.id || link.target) === node.id
        ).length;

        return Math.max(3, Math.min(10, connections / 2));
    };

    const handleZoomIn = () => {
        if (fgRef.current) {
            fgRef.current.zoom(fgRef.current.zoom() * 1.5, 400);
        }
    };

    const handleZoomOut = () => {
        if (fgRef.current) {
            fgRef.current.zoom(fgRef.current.zoom() / 1.5, 400);
        }
    };

    const togglePause = () => {
        if (fgRef.current) {
            if (isPaused) {
                fgRef.current.resumeAnimation();
            } else {
                fgRef.current.pauseAnimation();
            }
            setIsPaused(!isPaused);
        }
    };

    const filteredData = React.useMemo(() => {
        if (!searchQuery) return graphData;

        const query = searchQuery.toLowerCase();
        const matchingNodes = graphData.nodes.filter(node =>
            node.label.toLowerCase().includes(query) ||
            (node.item_id && node.item_id.toLowerCase().includes(query)) ||
            (node.metadata && node.metadata.topic && node.metadata.topic.toLowerCase().includes(query))
        );

        const matchingNodeIds = new Set(matchingNodes.map(n => n.id));
        const filteredLinks = graphData.links.filter(link =>
            matchingNodeIds.has(link.source.id || link.source) ||
            matchingNodeIds.has(link.target.id || link.target)
        );

        return { nodes: matchingNodes, links: filteredLinks };
    }, [graphData, searchQuery]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
                    <p className="text-slate-600 text-lg">Loading knowledge graph...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            <div className="container mx-auto px-4 py-6 max-w-full">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                            Knowledge Graph Visualization
                        </h1>
                        <p className="text-slate-600 mt-2">Interactive visualization - Use mouse to zoom (scroll) and pan (drag)</p>
                    </div>
                    <Button
                        variant="outline"
                        onClick={() => navigate('/')}
                        className="border-2"
                    >
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Home
                    </Button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    <div className="space-y-4">
                        {stats && (
                            <Card className="shadow-xl border-none bg-white/80 backdrop-blur">
                                <CardHeader>
                                    <div className="flex items-center gap-2">
                                        <Network className="h-5 w-5 text-blue-600" />
                                        <CardTitle className="text-lg">Graph Statistics</CardTitle>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-slate-600">Total Nodes:</span>
                                        <span className="font-semibold">{stats.total_nodes}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-600">Total Links:</span>
                                        <span className="font-semibold">{stats.total_links}</span>
                                    </div>
                                    <hr className="my-2" />
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-600">Items:</span>
                                        <span className="font-semibold text-blue-600">{stats.items}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-600">Topics:</span>
                                        <span className="font-semibold text-green-600">{stats.topics}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-600">Levels:</span>
                                        <span className="font-semibold text-orange-600">{stats.levels || 0}</span>
                                    </div>
                                    <hr className="my-2" />
                                    <div className="flex justify-between items-center text-xs">
                                        <span className="text-slate-500">Has Topic:</span>
                                        <span className="font-medium">{stats.has_topic_relations || 0}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-xs">
                                        <span className="text-slate-500">Has Level:</span>
                                        <span className="font-medium">{stats.has_level_relations || 0}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-xs">
                                        <span className="text-slate-500">Similar To:</span>
                                        <span className="font-medium">{stats.similar_relations || 0}</span>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        <Card className="shadow-xl border-none bg-white/80 backdrop-blur">
                            <CardHeader>
                                <CardTitle className="text-lg">Controls</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                                        Search
                                    </label>
                                    <Input
                                        placeholder="Search exercises or topics..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="border-2 focus:border-blue-400"
                                    />
                                </div>

                                <div>
                                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                                        Relationships: {limit}
                                    </label>
                                    <input
                                        type="range"
                                        min="100"
                                        max="10000"
                                        step="100"
                                        value={limit}
                                        onChange={(e) => setLimit(parseInt(e.target.value))}
                                        className="w-full"
                                    />
                                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                                        <span>100</span>
                                        <span>10000</span>
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <Button
                                        onClick={handleZoomIn}
                                        variant="outline"
                                        className="flex-1"
                                        size="sm"
                                    >
                                        <ZoomIn className="h-4 w-4" />
                                    </Button>
                                    <Button
                                        onClick={handleZoomOut}
                                        variant="outline"
                                        className="flex-1"
                                        size="sm"
                                    >
                                        <ZoomOut className="h-4 w-4" />
                                    </Button>
                                    <Button
                                        onClick={togglePause}
                                        variant="outline"
                                        className="flex-1"
                                        size="sm"
                                    >
                                        {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                                    </Button>
                                </div>

                                <div>
                                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                                        Legend
                                    </label>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                                            <span>Items (Exercises)</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full bg-green-500"></div>
                                            <span>Topics</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                                            <span>Difficulty Levels</span>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="lg:col-span-3">
                        <Card className="shadow-xl border-none bg-white/80 backdrop-blur overflow-hidden">
                            <CardContent className="p-0">
                                <div style={{ height: '700px', width: '100%' }}>
                                    <ForceGraph2D
                                        ref={fgRef}
                                        graphData={filteredData}
                                        nodeLabel={(node) => {
                                            if (node.type === 'item' && node.metadata) {
                                                return `${node.id}\nTopic: ${node.metadata.topic}\nLevel: ${node.metadata.level}`;
                                            }
                                            if (node.name) {
                                                return node.name;
                                            }
                                            return node.label;
                                        }}
                                        linkLabel={(link) => link.label || link.relation || ''}
                                        nodeColor={getNodeColor}
                                        nodeVal={getNodeSize}
                                        nodeRelSize={6}
                                        enableNodeDrag={true}
                                        enableZoomInteraction={true}
                                        enablePanInteraction={true}
                                        linkColor={link => highlightLinks.has(link) ? '#3b82f6' : '#cbd5e1'}
                                        linkWidth={link => highlightLinks.has(link) ? 2 : 1}
                                        linkDirectionalParticles={link => highlightLinks.has(link) ? 2 : 0}
                                        linkDirectionalParticleWidth={2}
                                        onNodeClick={handleNodeClick}
                                        onBackgroundClick={handleBackgroundClick}
                                        cooldownTicks={200}
                                        d3VelocityDecay={0.4}
                                        d3AlphaDecay={0.01}
                                        d3Force={{
                                            charge: { strength: -400, distanceMax: 500 },
                                            link: { distance: 30, strength: 1 },
                                            collision: { radius: 15 },
                                            center: { strength: 0.05 }
                                        }}
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
