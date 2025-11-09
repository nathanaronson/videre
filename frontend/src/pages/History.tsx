import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Video, Calendar, ArrowLeft, Play } from "lucide-react";
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
        if (!response.ok) {
          throw new Error("Failed to fetch chat histories");
        }
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
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-destructive/10 border border-destructive rounded-lg p-6 mb-4">
            <p className="text-destructive font-semibold mb-2">Error</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <Button onClick={() => navigate("/")}>Go Home</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-4xl font-bold mb-2">Video History</h1>
          <p className="text-muted-foreground">
            Browse your previously generated videos
          </p>
        </div>

        {/* History Grid */}
        {histories.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Video className="w-12 h-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground text-center">
                No videos generated yet. Create your first video!
              </p>
              <Button onClick={() => navigate("/")} className="mt-4">
                Generate Video
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {histories.map((history) => (
              <Card
                key={history.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleViewVideo(history)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between mb-2">
                    <Video className="w-5 h-5 text-primary" />
                    {history.video_url && (
                      <Play className="w-4 h-4 text-muted-foreground" />
                    )}
                  </div>
                  <CardTitle className="text-lg line-clamp-2">
                    {history.topic}
                  </CardTitle>
                  <CardDescription className="flex items-center gap-2 mt-2">
                    <Calendar className="w-3 h-3" />
                    {format(new Date(history.created_at), "MMM d, yyyy")}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {history.video_url ? (
                    <Button className="w-full" size="sm">
                      <Play className="w-4 h-4 mr-2" />
                      Watch Video
                    </Button>
                  ) : (
                    <p className="text-sm text-muted-foreground text-center py-2">
                      Video processing...
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
