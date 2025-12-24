import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { ChevronDown, ChevronUp, TrendingUp, Info, Sparkles, GitBranch } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function RecommendationCard({ recommendation, index, getDifficultyColor }) {
    const [showKgDetails, setShowKgDetails] = useState(false);
    const { external_id, score, info, kg_explanation } = recommendation;

    const hasKgExplanation = kg_explanation && kg_explanation.kg_context_text;

    // Check if explanation contains KGAT/KGIN analysis markers
    const hasEnhancedAnalysis = hasKgExplanation && (
        kg_explanation.kg_context_text.includes('KGAT') || 
        kg_explanation.kg_context_text.includes('EduKGAT') || 
        kg_explanation.kg_context_text.includes('KGIN') ||
        kg_explanation.kg_context_text.includes('trọng số')
    );

    return (
        <Card
            className="group hover:shadow-xl transition-all duration-300 border-2 border-slate-200 hover:border-blue-400 bg-white pt-5"
        >
            <CardContent className="py-8 px-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white font-bold shadow-lg">
                            {index + 1}
                        </div>
                        <div>
                            <h3 className="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition-colors">
                                {info.title || `Bài tập ${external_id}`}
                            </h3>
                            <p className="text-sm text-slate-500">ID: {external_id}</p>
                        </div>
                    </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-3">
                    <span className="px-3 py-1 text-sm rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                        {info.topic}
                    </span>
                    <span className={`px-3 py-1 text-sm rounded-full border ${getDifficultyColor(info.difficulty)}`}>
                        {info.difficulty}
                    </span>
                    {hasEnhancedAnalysis && (
                        <span className="px-3 py-1 text-xs rounded-full bg-purple-100 text-purple-800 border border-purple-200 flex items-center gap-1">
                            <Sparkles className="h-3 w-3" />
                            Phân tích EduKGAT
                        </span>
                    )}
                </div>

                {/* KG Explanation Section */}
                {hasKgExplanation && (
                    <div className="mt-4 border-t pt-4">
                        <button
                            onClick={() => setShowKgDetails(!showKgDetails)}
                            className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors w-full"
                        >
                            <Info className="h-4 w-4" />
                            <span>Tại sao gợi ý bài này? (Phân tích KG)</span>
                            {showKgDetails ? (
                                <ChevronUp className="h-4 w-4 ml-auto" />
                            ) : (
                                <ChevronDown className="h-4 w-4 ml-auto" />
                            )}
                        </button>

                        {showKgDetails && (
                            <div className="mt-3 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                                {/* Main explanation text */}
                                <div className="text-sm text-slate-700">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            h1: ({ node, ...props }) => <h1 className="text-lg font-bold text-blue-900 mb-2" {...props} />,
                                            h2: ({ node, ...props }) => <h2 className="text-md font-semibold text-blue-800 mt-3 mb-2" {...props} />,
                                            ul: ({ node, ...props }) => <ul className="list-disc pl-5 my-2 space-y-1" {...props} />,
                                            li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                                            strong: ({ node, ...props }) => <span className="font-semibold text-blue-800" {...props} />,
                                            p: ({ node, ...props }) => <p className="mb-2 last:mb-0 leading-relaxed" {...props} />,
                                            em: ({ node, ...props }) => <em className="text-slate-600 not-italic" {...props} />,
                                            code: ({ node, ...props }) => <code className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-mono" {...props} />,
                                        }}
                                    >
                                        {kg_explanation.kg_context_text}
                                    </ReactMarkdown>
                                </div>

                                {/* KG Paths visualization - Optional if paths exist in data */}
                                {kg_explanation.paths_from_history && kg_explanation.paths_from_history.length > 0 && (
                                    <div className="mt-4 pt-4 border-t border-blue-200">
                                        <div className="flex items-center gap-2 mb-2">
                                            <GitBranch className="h-4 w-4 text-blue-700" />
                                            <p className="text-xs font-semibold text-blue-800">Các đường dẫn tri thức:</p>
                                        </div>
                                        <div className="space-y-2">
                                            {kg_explanation.paths_from_history.slice(0, 3).map((pathInfo, idx) => (
                                                <div key={idx} className="text-xs text-slate-600 font-mono bg-white p-2 rounded border border-blue-200 overflow-x-auto">
                                                    {pathInfo.path_string}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
