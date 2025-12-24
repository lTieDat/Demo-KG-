import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
    const location = useLocation();
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
            
            // Get subject from location state or sessionStorage
            const subject = location.state?.subject || sessionStorage.getItem('currentSubject');
            const subjectParam = subject ? `&subject=${subject}` : '';
            
            const response = await api.get(`/graph/knowledge-graph?limit=${limit}${subjectParam}`);
            setGraphData(response.data);
            setStats(response.data.stats);
            toast({
                title: "✓ Tải Đồ thị thành công",
                description: `Đã tải ${response.data.stats.total_nodes} nút và ${response.data.stats.total_links} liên kết`,
                className: "bg-green-50 border-green-200 text-green-900",
            });
        } catch (error) {
            toast({
                title: "✗ Lỗi khi tải Đồ thị",
                description: error.response?.data?.detail || error.message,
                className: "bg-red-50 border-red-200 text-red-900",
            });
        } finally {
            setLoading(false);
        }
    };

    // Zoom controls
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

    // Node interactions
    const handleNodeClick = (node) => {
        // Collect neighbors
        const neighbors = new Set();
        const links = new Set();
        
        // Check all links to find partial or full neighbors
        // Efficient way: react-force-graph usually binds links to nodes objects (if graphData was mutated, checking structure)
        graphData.links.forEach(link => {
            const isSource = (link.source.id === node.id) || (link.source === node.id) || (link.source === node);
            const isTarget = (link.target.id === node.id) || (link.target === node.id) || (link.target === node);
            
            if (isSource || isTarget) {
                links.add(link);
                neighbors.add(link.source);
                neighbors.add(link.target);
            }
        });
        
        neighbors.add(node); // Include self
        
        setHighlightNodes(neighbors);
        setHighlightLinks(links);

        // Zoom to node
        if (fgRef.current) {
            fgRef.current.centerAt(node.x, node.y, 1000);
            fgRef.current.zoom(4, 1000);
        }
        
        toast({
            title: node.name || node.id,
            description: `Đã chọn: ${neighbors.size - 1} kết nối trực tiếp.`,
        });
    };

    const handleBackgroundClick = () => {
        // Reset view or highlight
        setHighlightNodes(new Set());
        setHighlightLinks(new Set());
    };
    
    // Filtering logic (simple version)
    const filteredData = React.useMemo(() => {
        if (!searchQuery) return graphData;
        
        const lowerQuery = searchQuery.toLowerCase();
        const filteredNodes = graphData.nodes.filter(node => 
            (node.name && node.name.toLowerCase().includes(lowerQuery)) ||
            (node.id && node.id.toLowerCase().includes(lowerQuery)) ||
            (node.metadata && node.metadata.topic && node.metadata.topic.toLowerCase().includes(lowerQuery))
        );
        
        const nodeIds = new Set(filteredNodes.map(n => n.id));
        const filteredLinks = graphData.links.filter(link => 
            nodeIds.has(link.source.id || link.source) && nodeIds.has(link.target.id || link.target)
        );
        
        return { nodes: filteredNodes, links: filteredLinks };
    }, [graphData, searchQuery]);

    // Graph styling
    const getNodeColor = (node) => {
        // If highlighting is active (set size > 0) and node is NOT in set, make it gray/transparent
        if (highlightNodes.size > 0 && !highlightNodes.has(node)) {
            return 'rgba(226, 232, 240, 0.1)'; // Very faint
        }
        
        if (node.type === 'item') return '#3b82f6'; // Blue
        if (node.type === 'topic') return '#22c55e'; // Green
        if (node.type === 'level') return '#f97316'; // Orange
        return '#94a3b8'; // Slate
    };
    
    const getNodeSize = (node) => {
        if (node.type === 'topic') return 8;
        if (node.type === 'item') return 5;
        return 3;
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
                    <p className="text-slate-600 text-lg">Đang tải Đồ thị Tri thức...</p>
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
                            Đồ thị Tri thức EduMatch
                        </h1>
                        <p className="text-slate-600 mt-2">Biểu diễn tương tác - Sử dụng chuột để phóng to (cuộn) và di chuyển (kéo thả)</p>
                    </div>
                    <Button
                        variant="outline"
                        onClick={() => navigate('/')}
                        className="border-2"
                    >
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Quay lại Trang chủ
                    </Button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    <div className="space-y-4">


                        <Card className="shadow-xl border-none bg-white/80 backdrop-blur">
                            <CardHeader>
                                <CardTitle className="text-lg">Điều khiển</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                                        Tìm kiếm
                                    </label>
                                    <Input
                                        placeholder="Tìm kiếm bài tập hoặc chủ đề..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="border-2 focus:border-blue-400"
                                    />
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
                                    {/* Reload Button */}
                                    <Button
                                        onClick={() => { setGraphData({nodes: [], links: []}); fetchGraphData(); }}
                                        variant="outline"
                                        className="flex-1"
                                        size="sm"
                                        title="Tải lại đồ thị"
                                    >
                                        <Loader2 className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                                    </Button>
                                </div>

                                <div>
                                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                                        Chú giải
                                    </label>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                                            <span>Bài tập</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full bg-green-500"></div>
                                            <span>Chủ đề</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                                            <span>Độ khó</span>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="lg:col-span-3">
                        <Card className="shadow-xl border-none bg-white/80 backdrop-blur overflow-hidden h-full">
                            <CardContent className="p-0 h-full">
                                <div style={{ height: 'calc(100vh - 140px)', width: '100%' }}>
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
                                        // Visual Effects
                                        linkColor={link => {
                                            if (highlightLinks.size > 0) {
                                                if (highlightLinks.has(link)) return 'rgba(0,0,0,0)'; // Hide (drawn custom)
                                                return 'rgba(203, 213, 225, 0.1)'; // Simple faint line for background
                                            }
                                            return '#cbd5e1'; // Default
                                        }}
                                        linkWidth={link => highlightLinks.has(link) ? 3 : 1}
                                        
                                        onNodeClick={handleNodeClick}
                                        onBackgroundClick={handleBackgroundClick}
                                        
                                        // Canvas Customization
                                        
                                        // 1. Draw highlighted links ON TOP with ANIMATION
                                        linkCanvasObjectMode={link => highlightLinks.has(link) ? 'after' : undefined}
                                        linkCanvasObject={(link, ctx) => {
                                            if (highlightLinks.has(link)) {
                                                const start = link.source;
                                                const end = link.target;
                                                
                                                if (typeof start !== 'object' || typeof end !== 'object') return;

                                                ctx.beginPath();
                                                ctx.moveTo(start.x, start.y);
                                                ctx.lineTo(end.x, end.y);
                                                
                                                ctx.lineWidth = 3;
                                                ctx.strokeStyle = '#2563eb'; // Bright blue
                                                
                                                // Animation: Marching Ants
                                                const dashLen = 8;
                                                const gapLen = 4;
                                                ctx.setLineDash([dashLen, gapLen]); 
                                                
                                                // Use performance.now for smooth animation
                                                const offset = (performance.now() / 50) % (dashLen + gapLen); 
                                                ctx.lineDashOffset = -offset; // Negative to move forward
                                                
                                                ctx.stroke();
                                                
                                                // Reset
                                                ctx.setLineDash([]);
                                                ctx.lineDashOffset = 0;
                                            }
                                        }}

                                        // 2. Draw highlighted node labels ON TOP
                                        nodeCanvasObjectMode={node => highlightNodes.has(node) ? 'after' : 'before'}
                                        nodeCanvasObject={(node, ctx, globalScale) => {
                                            // Dim non-highlighted nodes
                                            if (highlightNodes.size > 0 && !highlightNodes.has(node)) {
                                                // We can't easily "undraw" but relying on nodeColor returning light grey helps.
                                                // Use 'before' mode for non-highlighted to potentially draw a dimming circle?
                                                // Actually nodeColor handles the dimming.
                                                return; 
                                            }

                                            if (highlightNodes.has(node)) {
                                                const label = node.name || node.id;
                                                const fontSize = 14 / globalScale;
                                                const nodeR = getNodeSize(node);
                                                
                                                // Draw Glow/Halo
                                                ctx.beginPath();
                                                ctx.arc(node.x, node.y, nodeR + 6, 0, 2 * Math.PI);
                                                ctx.fillStyle = 'rgba(37, 99, 235, 0.2)'; // Faint blue glow
                                                ctx.fill();

                                                // Draw Node (Overwrite default to ensure it's on top and bright)
                                                ctx.beginPath();
                                                ctx.arc(node.x, node.y, nodeR, 0, 2 * Math.PI);
                                                ctx.fillStyle = getNodeColor(node); // Use correct color
                                                ctx.fill();
                                                ctx.strokeStyle = '#fff';
                                                ctx.lineWidth = 1.5;
                                                ctx.stroke();
                                                
                                                // Draw Label Bubble
                                                if (globalScale > 0.8) { // Only show labels when zoomed in a bit
                                                    ctx.font = `bold ${fontSize}px Sans-Serif`;
                                                    const textWidth = ctx.measureText(label).width;
                                                    const bckgDimensions = [textWidth + fontSize, fontSize * 1.4];
                                                    
                                                    // Draw bubble background (pill shape)
                                                    const bubbleX = node.x - bckgDimensions[0] / 2;
                                                    const bubbleY = node.y - nodeR - fontSize * 2;
                                                    
                                                    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
                                                    ctx.shadowColor = "rgba(0, 0, 0, 0.2)";
                                                    ctx.shadowBlur = 4;
                                                    
                                                    // Simple rect for speed, or rounded rect
                                                    ctx.fillRect(bubbleX, bubbleY, bckgDimensions[0], bckgDimensions[1]);
                                                    
                                                    ctx.shadowBlur = 0; // Reset
    
                                                    ctx.textAlign = 'center';
                                                    ctx.textBaseline = 'middle';
                                                    ctx.fillStyle = '#0f172a';
                                                    ctx.fillText(label, node.x, bubbleY + bckgDimensions[1]/2);
                                                }
                                            }
                                        }}
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
