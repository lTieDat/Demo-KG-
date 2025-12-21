import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Loader2, CheckCircle2, XCircle, ChevronRight } from "lucide-react";

export default function Home() {
    const [models, setModels] = useState({ compatible: [], incompatible: [] });
    const [loading, setLoading] = useState(true);
    const [loadingModel, setLoadingModel] = useState(null);
    const navigate = useNavigate();
    const { toast } = useToast();

    useEffect(() => {
        fetchModels();
    }, []);

    const fetchModels = async () => {
        try {
            const response = await api.get('/models');
            setModels(response.data);
        } catch (error) {
            toast({
                title: "✗ Error fetching models",
                description: error.message,
                className: "bg-red-50 border-red-200 text-red-900",
            });
        } finally {
            setLoading(false);
        }
    };

    const loadModel = async (filename) => {
        try {
            setLoadingModel(filename);
            await api.post('/models/load', { filename });
            toast({
                title: "✓ Model loaded successfully",
                description: `${filename} is ready to use`,
                className: "bg-green-50 border-green-200 text-green-900",
            });
            setTimeout(() => navigate('/dashboard'), 500);
        } catch (error) {
            toast({
                title: "✗ Error loading model",
                description: error.response?.data?.detail || error.message,
                className: "bg-red-50 border-red-200 text-red-900",
            });
            setLoadingModel(null);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
                    <p className="text-slate-600 text-lg">Loading models...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            <div className="container mx-auto px-4 py-12 max-w-6xl">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 mb-4">
                        EduMatch
                    </h1>
                    <p className="text-slate-600 text-lg mb-6">
                        AI-powered code exercise recommendations using Knowledge Graph Neural Networks
                    </p>
                    <Button
                        onClick={() => navigate('/graph')}
                        className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg"
                    >
                        <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                        </svg>
                        View Knowledge Graph
                    </Button>
                </div>

                {/* Compatible Models */}
                <Card className="mb-8 shadow-xl border-none bg-white/80 backdrop-blur">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="h-6 w-6 text-green-500" />
                            <CardTitle className="text-2xl">Compatible Models</CardTitle>
                        </div>
                        <CardDescription>Select a model to start generating recommendations</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {models.compatible.length === 0 ? (
                            <div className="text-center py-12">
                                <XCircle className="h-16 w-16 text-slate-300 mx-auto mb-4" />
                                <p className="text-slate-500 text-lg mb-2">No compatible models found</p>
                                <p className="text-slate-400 text-sm">Please ensure models are available in the saved directory</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {models.compatible.map((model) => (
                                    <div
                                        key={model.filename}
                                        className="group relative p-6 border-2 border-slate-200 rounded-xl hover:border-blue-400 hover:shadow-lg transition-all duration-300 bg-gradient-to-r from-white to-slate-50"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1">
                                                <h3 className="font-bold text-lg mb-2 text-slate-800 group-hover:text-blue-600 transition-colors">
                                                    {model.filename}
                                                </h3>
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                    <div>
                                                        <span className="text-slate-500">Score:</span>
                                                        <span className="ml-2 font-semibold text-blue-600">{model.info.score}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-500">Epoch:</span>
                                                        <span className="ml-2 font-semibold">{model.info.epoch}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-500">Dataset:</span>
                                                        <span className="ml-2 font-semibold">{model.info.dataset}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-500">Embedding:</span>
                                                        <span className="ml-2 font-semibold">{model.info.embedding_size}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <Button
                                                onClick={() => loadModel(model.filename)}
                                                disabled={loadingModel !== null}
                                                className="ml-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg"
                                            >
                                                {loadingModel === model.filename ? (
                                                    <>
                                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                        Loading...
                                                    </>
                                                ) : (
                                                    <>
                                                        Load Model
                                                        <ChevronRight className="ml-2 h-4 w-4" />
                                                    </>
                                                )}
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
