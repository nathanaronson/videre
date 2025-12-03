import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, ArrowLeft, Play } from "lucide-react";
import { format } from "date-fns";

interface ChatMessage {
  role: string;
  content: string;
  timestamp: string;
}

interface ChatHistoryItem {
  id: string;
  topic: string;
  video_url?: string;
  video_id?: string;
  created_at: string;
  updated_at: string;
  chat_messages: ChatMessage[];
}

const History = ({ setTopic, setVideoURL }: { setTopic: any; setVideoURL: any }) => {
  const navigate = useNavigate();
  const [histories, setHistories] = useState<ChatHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistories = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/chat-history");
        if (!response.ok) throw new Error("Failed to fetch");
        const data = await response.json();
        setHistories(data.chats);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };
    fetchHistories();
  }, []);

  const handleViewVideo = (history: ChatHistoryItem) => {
    if (history.video_url) {
      setTopic(history.topic);
      setVideoURL(history.video_url);
      navigate("/video");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center px-6">
        <p className="text-muted-foreground mb-4">{error}</p>
        <button
          onClick={() => navigate("/")}
          className="text-sm text-foreground hover:opacity-70"
        >
          Go back
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="p-6 flex justify-between items-center border-b border-border">
        <span className="text-sm font-medium tracking-tight">P2P</span>
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
      </header>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="text-2xl font-semibold tracking-tight mb-8">History</h1>

        {histories.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-muted-foreground mb-4">No videos yet</p>
            <button
              onClick={() => navigate("/")}
              className="text-sm px-4 py-2 bg-foreground text-background rounded-lg hover:opacity-90"
            >
              Create your first
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {histories.map((history) => (
              <button
                key={history.id}
                onClick={() => handleViewVideo(history)}
                disabled={!history.video_url}
                className="w-full text-left p-4 rounded-lg border border-border hover:bg-card transition-colors disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{history.topic}</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      {format(new Date(history.created_at), "MMM d, yyyy")}
                    </p>
                  </div>
                  {history.video_url && (
                    <Play className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors ml-4" />
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default History;
