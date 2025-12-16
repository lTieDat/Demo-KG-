import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Sparkles, User, BookOpen, TrendingUp, ArrowLeft, Search } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import RecommendationCard from '../components/RecommendationCard';

export default function Dashboard() {
    const [query, setQuery] = useState("");
    const [students, setStudents] = useState([]);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [recommendations, setRecommendations] = useState([]);
    const [kgAvailable, setKgAvailable] = useState(false);
    const [explanation, setExplanation] = useState("");
    const [loading, setLoading] = useState(false);
    const [explaining, setExplaining] = useState(false);
    const [searching, setSearching] = useState(false);
    const { toast } = useToast();

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            if (query) {
                searchStudents(query);
            } else {
                setStudents([]);
            }
        }, 300);
        return () => clearTimeout(timer);
    }, [query]);

    const searchStudents = async (q) => {
        try {
            setSearching(true);
            const response = await api.get(`/students?query=${q}`);
            setStudents(response.data.students);
        } catch (error) {
            console.error("Search error", error);
        } finally {
            setSearching(false);
        }
    };

    const handleSelectStudent = async (student) => {
        setSelectedStudent(student);
        setExplanation("");
        setQuery(student.code);
        setStudents([]);

        try {
            setLoading(true);
            // Use explained endpoint to get recommendations with KG context
            const response = await api.get(`/recommendations/${student.id}/explained?top_k=10`);
            setRecommendations(response.data.recommendations);
            setKgAvailable(response.data.kg_available);
            toast({
                title: "✓ Recommendations loaded",
                description: `Found ${response.data.recommendations.length} exercises for ${student.code}${response.data.kg_available ? ' with KG explanations' : ''}`,
                className: "bg-green-50 border-green-200 text-green-900",
            });
        } catch (error) {
            toast({
                title: "✗ Error fetching recommendations",
                description: error.message,
                className: "bg-red-50 border-red-200 text-red-900",
            });
        } finally {
            setLoading(false);
        }
    };

    const getExplanation = async () => {
        if (!selectedStudent || recommendations.length === 0) return;

        try {
            setExplaining(true);
            const response = await api.post('/recommendations/explain', {
                student_code: selectedStudent.code,
                recommendations: recommendations,
                service: "kg"
            });
            setExplanation(response.data.explanation);
            toast({
                title: "✓ AI Analysis Complete",
                description: "Explanation generated successfully",
                className: "bg-green-50 border-green-200 text-green-900",
            });
        } catch (error) {
            toast({
                title: "✗ Error generating explanation",
                description: error.response?.data?.detail || error.message,
                className: "bg-red-50 border-red-200 text-red-900",
            });
        } finally {
            setExplaining(false);
        }
    };

    const getDifficultyColor = (difficulty) => {
        const colors = {
            'Easy': 'bg-green-100 text-green-800 border-green-200',
            'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'Hard': 'bg-red-100 text-red-800 border-red-200',
        };
        return colors[difficulty] || 'bg-gray-100 text-gray-800 border-gray-200';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            <div className="container mx-auto px-4 py-8 max-w-7xl">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                            Dashboard
                        </h1>
                        <p className="text-slate-600 mt-2">Personalized exercise recommendations</p>
                    </div>
                    <Button
                        variant="outline"
                        onClick={() => window.location.href = '/'}
                        className="border-2"
                    >
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Change Model
                    </Button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column: Student Selection & Actions */}
                    <div className="space-y-6">
                        <Card className="shadow-xl border-none bg-white/80 backdrop-blur">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <User className="h-5 w-5 text-blue-600" />
                                    <CardTitle>Select Student</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="relative">
                                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                                        Search by Student Code
                                    </label>
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                                        <Input
                                            placeholder="Type to search (e.g., B21DCAT...)"
                                            value={query}
                                            onChange={(e) => setQuery(e.target.value)}
                                            className="pl-10 border-2 focus:border-blue-400"
                                        />
                                        {searching && (
                                            <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 animate-spin text-blue-600" />
                                        )}
                                    </div>

                                    {/* Search Results Dropdown */}
                                    {students.length > 0 && (
                                        <div className="absolute z-10 w-full mt-2 bg-white border-2 border-blue-200 rounded-lg shadow-xl max-h-64 overflow-y-auto">
                                            {students.map((student) => (
                                                <button
                                                    key={student.id}
                                                    onClick={() => handleSelectStudent(student)}
                                                    className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors border-b border-slate-100 last:border-b-0"
                                                >
                                                    <div className="font-semibold text-slate-800">{student.code}</div>
                                                    <div className="text-xs text-slate-500">ID: {student.id}</div>
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {selectedStudent && (
                                    <div className="pt-4 border-t">
                                        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200">
                                            <p className="text-sm text-slate-600 mb-1">Selected:</p>
                                            <p className="font-bold text-lg text-blue-700">{selectedStudent.code}</p>
                                            <p className="text-xs text-slate-500">ID: {selectedStudent.id}</p>
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        {selectedStudent && recommendations.length > 0 && (
                            <Card className="shadow-xl border-none bg-gradient-to-br from-purple-50 to-pink-50">
                                <CardHeader>
                                    <div className="flex items-center gap-2">
                                        <Sparkles className="h-5 w-5 text-purple-600" />
                                        <CardTitle>AI Analysis</CardTitle>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <Button
                                        className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg"
                                        onClick={getExplanation}
                                        disabled={explaining}
                                    >
                                        {explaining ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Analyzing...
                                            </>
                                        ) : (
                                            <>
                                                <Sparkles className="mr-2 h-4 w-4" />
                                                Get AI Explanation
                                            </>
                                        )}
                                    </Button>
                                </CardContent>
                            </Card>
                        )}
                    </div>

                    {/* Right Column: Recommendations & Explanation */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* AI Explanation */}
                        {explanation && (
                            <Card className="shadow-xl border-none bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
                                <CardHeader>
                                    <div className="flex items-center gap-2">
                                        <Sparkles className="h-5 w-5 text-purple-600" />
                                        <CardTitle className="text-purple-700">AI Analysis</CardTitle>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="prose prose-sm max-w-none">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                h1: ({ node, ...props }) => <h1 className="text-2xl font-bold text-purple-800 mb-4 mt-6" {...props} />,
                                                h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-purple-700 mb-3 mt-5" {...props} />,
                                                h3: ({ node, ...props }) => <h3 className="text-lg font-semibold text-purple-600 mb-2 mt-4" {...props} />,
                                                h4: ({ node, ...props }) => <h4 className="text-base font-semibold text-purple-600 mb-2 mt-3" {...props} />,
                                                p: ({ node, ...props }) => <p className="text-slate-700 mb-3 leading-relaxed" {...props} />,
                                                ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-3 space-y-1 text-slate-700" {...props} />,
                                                ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-3 space-y-1 text-slate-700" {...props} />,
                                                li: ({ node, ...props }) => <li className="ml-4" {...props} />,
                                                strong: ({ node, ...props }) => <strong className="font-bold text-slate-800" {...props} />,
                                                em: ({ node, ...props }) => <em className="italic text-slate-700" {...props} />,
                                                code: ({ node, inline, ...props }) =>
                                                    inline
                                                        ? <code className="bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
                                                        : <code className="block bg-slate-800 text-slate-100 p-4 rounded-lg mb-3 overflow-x-auto font-mono text-sm" {...props} />,
                                                blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-purple-400 pl-4 italic text-slate-600 my-3" {...props} />,
                                                hr: ({ node, ...props }) => <hr className="my-6 border-purple-200" {...props} />,
                                            }}
                                        >
                                            {explanation}
                                        </ReactMarkdown>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Recommendations */}
                        {loading ? (
                            <div className="flex justify-center items-center py-24">
                                <div className="text-center">
                                    <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
                                    <p className="text-slate-600">Loading recommendations...</p>
                                </div>
                            </div>
                        ) : recommendations.length > 0 ? (
                            <div className="space-y-4">
                                <div className="flex items-center gap-2 mb-4">
                                    <BookOpen className="h-5 w-5 text-blue-600" />
                                    <h2 className="text-xl font-semibold text-slate-800">
                                        Recommended Exercises ({recommendations.length})
                                    </h2>
                                </div>
                                <div className="grid gap-4">
                                    {recommendations.map((rec, index) => (
                                        <RecommendationCard
                                            key={rec.internal_id}
                                            recommendation={rec}
                                            index={index}
                                            getDifficultyColor={getDifficultyColor}
                                        />
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <Card className="shadow-xl border-none bg-white/60 backdrop-blur">
                                <CardContent className="py-24">
                                    <div className="text-center">
                                        <BookOpen className="h-16 w-16 text-slate-300 mx-auto mb-4" />
                                        <p className="text-slate-500 text-lg">Search and select a student to view recommendations</p>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
