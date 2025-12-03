import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus } from 'lucide-react';

const VideoDisplay = ({ topic, videoURL }: { topic: string, videoURL: string }) => {
  const navigate = useNavigate();

  if (!topic || !videoURL) {
    navigate('/');
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="p-6 flex justify-between items-center border-b border-border">
        <span className="text-sm font-medium tracking-tight">P2P</span>
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/history')}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            History
          </button>
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Title */}
        <h1 className="text-2xl font-semibold tracking-tight mb-6">{topic}</h1>

        {/* Video */}
        <div className="bg-black rounded-lg overflow-hidden mb-6">
          <video
            controls
            autoPlay
            className="w-full aspect-video"
            src={videoURL}
          >
            Your browser does not support the video tag.
          </video>
        </div>

        {/* Action */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 px-4 py-2 bg-foreground text-background rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          New video
        </button>
      </main>
    </div>
  );
};

export default VideoDisplay;
