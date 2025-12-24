import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import RecommendationCard from '../components/RecommendationCard';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { 
    BookOpen, Search, LogOut, Code2, 
    LayoutDashboard, User, Loader2, Sparkles, Network 
} from "lucide-react";

export default function Dashboard() {
    const [students, setStudents] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [recommendations, setRecommendations] = useState([]);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [loading, setLoading] = useState(false);
    const [searching, setSearching] = useState(false);
    
    // Get subject from session storage (set in Home.jsx)
    const currentSubject = sessionStorage.getItem('currentSubject') || 'cpp';
    const subjectName = currentSubject === 'algorithm' ? 'Cấu trúc dữ liệu & Giải thuật' : 'Lập trình C++';
    
    const navigate = useNavigate();
    const { toast } = useToast();

    // Load students on mount or search
    useEffect(() => {
        searchStudents();
    }, [searchQuery]); // Debouncing would be better but keep simple

    const searchStudents = async () => {
        try {
            setSearching(true);
            const response = await api.get(`/students?query=${searchQuery}&limit=10`);
            setStudents(response.data);
        } catch (error) {
            console.error("Error searching students:", error);
        } finally {
            setSearching(false);
        }
    };

    const [history, setHistory] = useState([]);
    const [historySearchQuery, setHistorySearchQuery] = useState('');

    // ... (existing code)

    const handleStudentSelect = async (student) => {
        setSelectedStudent(student);
        setHistorySearchQuery('');
        setLoading(true);
        try {
            // Parallel fetch: Recs and History
            const [recsRes, histRes] = await Promise.all([
                api.get(`/recommendations/${student.id}/explained?k=5`),
                api.get(`/${student.id}/history`)
            ]);

            setRecommendations(recsRes.data);
            setHistory(histRes.data);
            
            toast({
                title: "✓ Đã tải dữ liệu",
                description: `Tìm thấy ${recsRes.data.length} gợi ý và ${histRes.data.length} bài đã làm`,
                className: "bg-green-50 border-green-200 text-green-900",
            });
        } catch (error) {
            toast({
                title: "✗ Lỗi tải gợi ý",
                description: error.response?.data?.detail || "Không thể tải danh sách gợi ý",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const getDifficultyColor = (difficulty) => {
        const colors = {
            'Easy': 'bg-green-100 text-green-800 border-green-200',
            'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'Hard': 'bg-red-100 text-red-800 border-red-200'
        };
        return colors[difficulty] || 'bg-slate-100 text-slate-800 border-slate-200';
    };
    
    const handleViewGraph = () => {
         navigate('/graph', { state: { subject: currentSubject } });
    };

    const filteredHistory = history.filter(item => {
        if (!historySearchQuery) return true;
        const query = historySearchQuery.toLowerCase();
        return (
            (item.name && item.name.toLowerCase().includes(query)) ||
            (item.id && item.id.toString().toLowerCase().includes(query)) ||
            (item.topic && item.topic.toLowerCase().includes(query))
        );
    });

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur border-b sticky top-0 z-10 shadow-sm">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                            <Code2 className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h1 className="font-bold text-xl text-slate-800">EduMatch Dashboard</h1>
                            <p className="text-xs text-slate-500 font-medium bg-blue-50 px-2 py-0.5 rounded-full inline-block border border-blue-100">
                                {subjectName}
                            </p>
                        </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                        <Button 
                            variant="outline" 
                            size="sm"
                            onClick={handleViewGraph}
                            className="hidden md:flex"
                        >
                            <Network className="mr-2 h-4 w-4" />
                            Xem Đồ thị
                        </Button>
                        <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => navigate('/')}
                            className="text-slate-600 hover:text-red-600 hover:bg-red-50"
                        >
                            <LogOut className="mr-2 h-4 w-4" />
                            Thoát
                        </Button>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8 max-w-7xl">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left Sidebar: Student Search */}
                    <div className="lg:col-span-4 space-y-6">
                        <Card className="shadow-lg border-none bg-white/80 backdrop-blur">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-lg">
                                    <User className="h-5 w-5 text-blue-500" />
                                    Chọn Sinh viên
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="relative">
                                    <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                    <Input 
                                        placeholder="Tìm kiếm theo ID..." 
                                        className="pl-9 bg-slate-50 border-slate-200 focus:bg-white transition-all"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                    />
                                </div>
                                
                                <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                                    {searching ? (
                                        <div className="flex justify-center p-4">
                                            <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                                        </div>
                                    ) : students.length > 0 ? (
                                        students.map((student) => (
                                            <button
                                                key={student.id}
                                                onClick={() => handleStudentSelect(student)}
                                                className={`w-full text-left p-3 rounded-xl transition-all duration-200 flex items-center gap-3
                                                    ${selectedStudent?.id === student.id 
                                                        ? 'bg-blue-600 text-white shadow-md transform scale-[1.02]' 
                                                        : 'hover:bg-blue-50 text-slate-700 hover:pl-4'
                                                    }`}
                                            >
                                                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs
                                                    ${selectedStudent?.id === student.id ? 'bg-white/20 text-white' : 'bg-blue-100 text-blue-600'}`}>
                                                    {(student.student_id || student.id).slice(0, 2)}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="font-medium truncate">{student.name}</p>
                                                    <p className={`text-xs ${selectedStudent?.id === student.id ? 'text-blue-100' : 'text-slate-500'}`}>
                                                        ID: {student.student_id || student.id}
                                                    </p>
                                                </div>
                                            </button>
                                        ))
                                    ) : (
                                        <p className="text-center text-slate-500 text-sm py-8">
                                            Không tìm thấy sinh viên
                                        </p>
                                    )}
                                </div>
                            </CardContent>
                        </Card>

                        {/* History Section */}
                        {selectedStudent && (
                            <Card className="shadow-lg border-none bg-white/80 backdrop-blur">
                                <CardHeader>
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="flex items-center gap-2 text-lg">
                                            <BookOpen className="h-5 w-5 text-indigo-500" />
                                            Lịch sử làm bài
                                        </CardTitle>
                                        <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                                            {filteredHistory.length}/{history.length}
                                        </span>
                                    </div>
                                    <div className="mt-3 relative">
                                        <Search className="absolute left-2 top-2.5 h-3 w-3 text-slate-400" />
                                        <Input
                                            placeholder="Tìm bài đã làm..."
                                            className="h-8 pl-7 text-xs bg-slate-50"
                                            value={historySearchQuery}
                                            onChange={(e) => setHistorySearchQuery(e.target.value)}
                                        />
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                        {filteredHistory.length > 0 ? (
                                            filteredHistory.map((item, idx) => (
                                                <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex justify-between items-center group hover:bg-white hover:border-indigo-200 transition-all">
                                                    <div>
                                                        <p className="font-medium text-sm text-slate-700 group-hover:text-indigo-700">{item.name}</p>
                                                        <p className="text-xs text-slate-500">{item.id} • {item.topic}</p>
                                                    </div>
                                                    <span className={`text-[10px] px-2 py-0.5 rounded border ${getDifficultyColor(item.difficulty)} opacity-70`}>
                                                        {item.difficulty}
                                                    </span>
                                                </div>
                                            ))
                                        ) : (
                                            <p className="text-center text-slate-500 text-sm py-4">Chưa có dữ liệu lịch sử</p>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>

                    {/* Right Content: Recommendations */}
                    <div className="lg:col-span-8">
                        {loading ? (
                            <div className="flex justify-center items-center py-24">
                                <div className="text-center">
                                    <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
                                    <p className="text-slate-600">Đang tìm kiếm gợi ý...</p>
                                </div>
                            </div>
                        ) : recommendations.length > 0 ? (
                            <div className="space-y-4">
                                <div className="flex items-center gap-2 mb-4">
                                    <BookOpen className="h-5 w-5 text-blue-600" />
                                    <h2 className="text-xl font-semibold text-slate-800">
                                        Bài tập Gợi ý ({recommendations.length})
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
                                        <Sparkles className="h-16 w-16 text-slate-300 mx-auto mb-4" />
                                        <h3 className="text-xl font-semibold text-slate-600 mb-2">
                                            Chọn sinh viên để bắt đầu
                                        </h3>
                                        <p className="text-slate-500 max-w-md mx-auto">
                                            Tìm kiếm sinh viên bên trái để xem các bài tập được gợi ý từ AI
                                        </p>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
