import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { BookOpen, Code2, Loader2, CheckCircle2, ChevronRight, ArrowLeft, XCircle, Network } from "lucide-react";

// Subject Configuration
const SUBJECTS = {
    'algorithm': {
        name: 'Cấu trúc dữ liệu & Giải thuật',
        description: 'Các bài tập về cấu trúc dữ liệu và giải thuật',
        icon: BookOpen,
        color: 'from-purple-500 to-indigo-600',
        bgColor: 'from-purple-50 to-indigo-50',
        borderColor: 'border-purple-200'
    },
    'cpp': {
        name: 'Lập trình C++',
        description: 'Các bài tập lập trình ngôn ngữ C++',
        icon: Code2,
        color: 'from-blue-500 to-cyan-600',
        bgColor: 'from-blue-50 to-cyan-50',
        borderColor: 'border-blue-200'
    }
};

export default function Home() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedSubject, setSelectedSubject] = useState(null);
    const [loadingModel, setLoadingModel] = useState(null);
    const navigate = useNavigate();
    const { toast } = useToast();

    useEffect(() => {
        fetchModels();
    }, []);

    const fetchModels = async () => {
        try {
            const response = await api.get('/models');
            // Combine compatible and incompatible lists for display
            const allModels = [
                ...(response.data.compatible || []),
                ...(response.data.incompatible || [])
            ];
            setModels(allModels);
        } catch (error) {
            toast({
                title: "Error fetching models",
                description: "Could not load available models",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const getModelsForSubject = (subjectKey) => {
        return models.filter(model => {
            const filename = model.filename.toLowerCase();
            if (subjectKey === 'algorithm') {
                return filename.includes('algo') || filename.includes('ctdl');
            } else if (subjectKey === 'cpp') {
                return filename.includes('cpp');
            }
            return false;
        });
    };

    const loadModel = async (filename) => {
        try {
            setLoadingModel(filename);
            await api.post('/models/load', { filename });
            toast({
                title: "✓ Tải mô hình thành công",
                description: `${filename} đã sẵn sàng để sử dụng`,
                className: "bg-green-50 border-green-200 text-green-900",
            });
            // Store selected subject in sessionStorage for Dashboard
            sessionStorage.setItem('currentSubject', selectedSubject);
            setTimeout(() => navigate('/dashboard'), 500);
        } catch (error) {
            toast({
                title: "✗ Lỗi khi tải mô hình",
                description: error.response?.data?.detail || error.message,
                className: "bg-red-50 border-red-200 text-red-900",
            });
            setLoadingModel(null);
        }
    };

    const handleViewGraph = () => {
        // When viewing graph from subject selection, we need to pass the subject context
        // We can do this by setting sessionStorage or query param
        // For simplicity and consistency with Dashboard, we'll try setting sessionStorage
        // But better yet, if the graph page supports query param, that's safer.
        // We updated graph page to read from sessionStorage usually, but let's set it here just in case.
        if (selectedSubject) {
            sessionStorage.setItem('currentSubject', selectedSubject);
            // Also navigate with state in case we want to read it from location
            navigate('/graph', { state: { subject: selectedSubject } });
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
                    <p className="text-slate-600 text-lg">Đang tải danh sách mô hình...</p>
                </div>
            </div>
        );
    }

    // Step 1: Subject Selection
    if (!selectedSubject) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
                <div className="container mx-auto px-4 py-12 max-w-6xl">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 mb-4">
                            EduMatch
                        </h1>
                        <p className="text-slate-600 text-lg mb-2">
                            Hệ thống gợi ý bài tập thông minh sử dụng Mạng nơ-ron Đồ thị Tri thức
                        </p>
                        <p className="text-slate-500">
                            Chọn môn học để bắt đầu
                        </p>
                    </div>

                    {/* Subject Selection */}
                    <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                        {Object.entries(SUBJECTS).map(([key, subject]) => {
                            const Icon = subject.icon;
                            const modelCount = getModelsForSubject(key).length;
                            
                            return (
                                <button
                                    key={key}
                                    onClick={() => setSelectedSubject(key)}
                                    className={`group relative p-8 rounded-2xl border-2 ${subject.borderColor} 
                                        bg-gradient-to-br ${subject.bgColor} 
                                        hover:shadow-2xl hover:scale-[1.02] transition-all duration-300
                                        text-left`}
                                >
                                    <div className="flex items-start gap-4">
                                        <div className={`p-4 rounded-xl bg-gradient-to-r ${subject.color} shadow-lg`}>
                                            <Icon className="h-8 w-8 text-white" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="text-2xl font-bold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors">
                                                {subject.name}
                                            </h3>
                                            <p className="text-slate-600 mb-4">
                                                {subject.description}
                                            </p>
                                            <div className="flex items-center gap-2 text-sm">
                                                <CheckCircle2 className={`h-4 w-4 ${modelCount > 0 ? 'text-green-500' : 'text-slate-400'}`} />
                                                <span className={`${modelCount > 0 ? 'text-slate-600' : 'text-slate-400'}`}>
                                                    {modelCount} mô hình khả dụng
                                                </span>
                                            </div>
                                        </div>
                                        <ChevronRight className="h-6 w-6 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>
        );
    }

    // Step 2: Model Selection for chosen subject
    const subjectConfig = SUBJECTS[selectedSubject];
    const SubjectIcon = subjectConfig.icon;
    const filteredModels = getModelsForSubject(selectedSubject);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            <div className="container mx-auto px-4 py-12 max-w-6xl">
                {/* Header with back button */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <Button
                            variant="ghost"
                            onClick={() => setSelectedSubject(null)}
                            className="p-2"
                        >
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                        <div>
                            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                                EduMatch
                            </h1>
                            <div className="flex items-center gap-2 mt-1">
                                <SubjectIcon className="h-4 w-4 text-slate-500" />
                                <span className="text-slate-600">{subjectConfig.name}</span>
                            </div>
                        </div>
                    </div>

                    {/* KG Visualization Button - Subject Specific */}
                    <Button
                        onClick={handleViewGraph}
                        variant="outline"
                        className="bg-white hover:bg-slate-50 text-blue-600 border-2 border-blue-200"
                    >
                        <Network className="mr-2 h-4 w-4" />
                        Xem Đồ thị Tri thức
                    </Button>
                </div>

                {/* Models for selected subject */}
                <Card className="shadow-xl border-none bg-white/80 backdrop-blur">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="h-6 w-6 text-green-500" />
                            <CardTitle className="text-2xl">Chọn Mô hình</CardTitle>
                        </div>
                        <CardDescription>
                            Chọn mô hình đã huấn luyện cho môn {subjectConfig.name}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {filteredModels.length === 0 ? (
                            <div className="text-center py-12">
                                <XCircle className="h-16 w-16 text-slate-300 mx-auto mb-4" />
                                <p className="text-slate-500 text-lg mb-2">Không tìm thấy mô hình nào cho môn học này</p>
                                <p className="text-slate-400 text-sm">Vui lòng đảm bảo các file mô hình (.pth) đã được lưu trong thư mục saved</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {filteredModels.map((model) => (
                                    <div
                                        key={model.filename}
                                        className={`group relative py-8 px-6 border-2 rounded-xl hover:shadow-lg transition-all duration-300 
                                            bg-gradient-to-r from-white to-slate-50 ${subjectConfig.borderColor} hover:border-blue-400`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1">
                                                <h3 className="font-bold text-lg mb-2 text-slate-800 group-hover:text-blue-600 transition-colors">
                                                    {model.filename}
                                                </h3>
                                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                                    <div>
                                                        <span className="text-slate-500">Epoch:</span>
                                                        <span className="ml-2 font-semibold">{model.info.epoch}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-500">Model:</span>
                                                        <span className="ml-2 font-semibold">{model.info.model_type || 'EduKGAT'}</span>
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
                                                className={`ml-6 bg-gradient-to-r ${subjectConfig.color} hover:opacity-90 text-white shadow-lg`}
                                            >
                                                {loadingModel === model.filename ? (
                                                    <>
                                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                        Đang tải...
                                                    </>
                                                ) : (
                                                    <>
                                                        Tải Mô hình
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
