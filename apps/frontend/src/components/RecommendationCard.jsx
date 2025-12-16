import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { ChevronDown, ChevronUp, TrendingUp, Info } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function RecommendationCard({ recommendation, index, getDifficultyColor }) {
    const [showKgDetails, setShowKgDetails] = useState(false);
    const { external_id, score, info, kg_explanation } = recommendation;

    const hasKgExplanation = kg_explanation && kg_explanation.kg_context_text;

    return (
        <Card
            className="group hover:shadow-xl transition-all duration-300 border-2 border-slate-200 hover:border-blue-400 bg-white"
        >
            <CardContent className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white font-bold shadow-lg">
                            {index + 1}
                        </div>
                        <div>
                            <h3 className="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition-colors">
                                {info.title}
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
                </div>

                {/* KG Explanation Section */}
                {hasKgExplanation && (
                    <div className="mt-4 border-t pt-4">
                        <button
                            onClick={() => setShowKgDetails(!showKgDetails)}
                            className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors w-full"
                        >
                            <Info className="h-4 w-4" />
                            <span>Tại sao gợi ý bài này? (KG)</span>
                            {showKgDetails ? (
                                <ChevronUp className="h-4 w-4 ml-auto" />
                            ) : (
                                <ChevronDown className="h-4 w-4 ml-auto" />
                            )}
                        </button>

                        {showKgDetails && (
                            <div className="mt-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                                <div className="text-sm text-slate-700">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            ul: ({ node, ...props }) => <ul className="list-disc pl-5 my-2 space-y-1" {...props} />,
                                            li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                                            strong: ({ node, ...props }) => <span className="font-semibold text-blue-800" {...props} />,
                                            p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />
                                        }}
                                    >
                                        {kg_explanation.kg_context_text}
                                    </ReactMarkdown>
                                </div>

                                {/* Show paths if available */}
                                {kg_explanation.paths_from_history && kg_explanation.paths_from_history.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-blue-300">
                                        <p className="text-xs font-semibold text-blue-800 mb-2">Knowledge Graph Paths:</p>
                                        {kg_explanation.paths_from_history.slice(0, 3).map((pathInfo, idx) => (
                                            <div key={idx} className="text-xs text-slate-600 mb-1 font-mono bg-white p-2 rounded border border-blue-200">
                                                {pathInfo.path_string}
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Show shared entities if available */}
                                {kg_explanation.shared_entities && kg_explanation.shared_entities.length > 0 && (
                                    <div className="mt-2">
                                        <p className="text-xs font-semibold text-blue-800 mb-1">Connections:</p>
                                        {kg_explanation.shared_entities.slice(0, 3).map((entity, idx) => (
                                            <div key={idx} className="text-xs text-slate-600">
                                                • Related to {entity.from_item}
                                                {entity.shared.topics && entity.shared.topics.length > 0 && (
                                                    <span> (same topic)</span>
                                                )}
                                                {entity.shared.levels && entity.shared.levels.length > 0 && (
                                                    <span> (same level)</span>
                                                )}
                                            </div>
                                        ))}
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
