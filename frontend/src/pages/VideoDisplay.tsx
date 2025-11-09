import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Download, Home, Share2, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';

const VideoDisplay = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { videoUrl, topic } = location.state || {};

  if (!videoUrl) {
    navigate('/');
    return null;
  }

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `Videre: ${topic}`,
        text: `Check out this educational video about ${topic}`,
        url: videoUrl,
      }).catch(() => {
        // User cancelled share
      });
    } else {
      navigator.clipboard.writeText(videoUrl);
      toast.success('Video URL copied to clipboard!');
    }
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = `${topic.replace(/\s+/g, '_')}_video.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Download started!');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">
            <span className="text-gradient">Videre</span>
          </h1>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Home
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 md:py-12">
        <div className="max-w-5xl mx-auto">
          {/* Video Info */}
          <div className="mb-6">
            <h2 className="text-3xl font-bold mb-2">{topic}</h2>
            <p className="text-muted-foreground">
              Your educational video is ready to watch
            </p>
          </div>

          {/* Video Player */}
          <div className="bg-black rounded-2xl overflow-hidden shadow-2xl mb-6">
            <video
              controls
              className="w-full aspect-video"
              src={videoUrl}
              autoPlay
            >
              Your browser does not support the video tag.
            </video>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 justify-center">
            <Button
              variant="default"
              onClick={handleDownload}
              className="flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download Video
            </Button>
            <Button
              variant="outline"
              onClick={handleShare}
              className="flex items-center gap-2"
            >
              <Share2 className="w-4 h-4" />
              Share
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/')}
              className="flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Create Another
            </Button>
          </div>

          {/* Video Description */}
          <div className="mt-12 bg-card border border-border rounded-xl p-6">
            <h3 className="font-semibold mb-2">About this video</h3>
            <p className="text-sm text-muted-foreground">
              This video was generated using AI-powered educational content creation.
              The animations were created with Manim, a mathematical animation engine,
              and the narration was synthesized to provide clear, step-by-step explanations
              of complex concepts.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoDisplay;
