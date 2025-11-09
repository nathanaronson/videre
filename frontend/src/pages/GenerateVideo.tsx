import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Loader2, Sparkles, Video, CheckCircle2 } from 'lucide-react';

interface GenerationStep {
  id: string;
  label: string;
  status: 'pending' | 'processing' | 'completed';
}

const GenerateVideo = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { topic, inputMode, file } = location.state || {};

  const [steps, setSteps] = useState<GenerationStep[]>([
    { id: 'analyzing', label: 'Analyzing your topic...', status: 'pending' },
    { id: 'script', label: 'Generating educational script...', status: 'pending' },
    { id: 'manim', label: 'Creating animations with Manim...', status: 'pending' },
    { id: 'voiceover', label: 'Generating voiceover...', status: 'pending' },
    { id: 'rendering', label: 'Rendering final video...', status: 'pending' },
    { id: 'uploading', label: 'Uploading to AWS...', status: 'pending' },
  ]);

  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!topic) {
      navigate('/');
      return;
    }

    // Start the video generation process
    generateVideo();
  }, [topic]);

  const generateVideo = async () => {
    try {
      // Simulate step progression for UI feedback
      // Steps progress every 8 seconds (6 steps = ~48 seconds total)
      const stepProgressionInterval = setInterval(() => {
        setSteps(prev => {
          const currentProcessingIndex = prev.findIndex(s => s.status === 'processing');
          const currentPendingIndex = prev.findIndex(s => s.status === 'pending');

          if (currentProcessingIndex !== -1) {
            // Don't progress past the last step until we get a response
            if (currentProcessingIndex === prev.length - 1) {
              return prev; // Keep last step processing
            }
            // Mark current as completed and move to next
            return prev.map((step, idx) => ({
              ...step,
              status: idx < currentProcessingIndex ? 'completed' :
                      idx === currentProcessingIndex ? 'completed' :
                      idx === currentProcessingIndex + 1 ? 'processing' :
                      'pending'
            }));
          } else if (currentPendingIndex === 0) {
            // Start first step
            return prev.map((step, idx) => ({
              ...step,
              status: idx === 0 ? 'processing' : 'pending'
            }));
          }
          return prev;
        });
      }, 8000);

      // Make actual API call to backend
      const response = await fetch('http://localhost:8000/api/integrate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      clearInterval(stepProgressionInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate video');
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error('Video generation failed');
      }

      // Mark all steps as completed
      setSteps(prev => prev.map(step => ({ ...step, status: 'completed' })));

      // Use the video URL from the backend response
      setVideoUrl(data.video_url);

      // Navigate to video display after a short delay
      setTimeout(() => {
        navigate('/video', { state: { videoUrl: data.video_url, topic } });
      }, 1500);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Video generation error:', err);
    }
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-muted" />;
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-destructive/10 border border-destructive rounded-lg p-6 mb-4">
            <p className="text-destructive font-semibold mb-2">Error</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <button
            onClick={() => navigate('/')}
            className="text-primary hover:underline"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-8 h-8 text-primary animate-pulse" />
            <Video className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold mb-2">Creating Your Video</h1>
          <p className="text-muted-foreground">
            Generating educational content about: <span className="font-semibold text-foreground">{topic}</span>
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className="flex items-center gap-4 transition-all duration-300"
              >
                <div className="flex-shrink-0">
                  {getStepIcon(step.status)}
                </div>
                <div className="flex-1">
                  <p className={`text-sm font-medium ${
                    step.status === 'completed' ? 'text-muted-foreground line-through' :
                    step.status === 'processing' ? 'text-primary' :
                    'text-muted-foreground'
                  }`}>
                    {step.label}
                  </p>
                </div>
                {step.status === 'processing' && (
                  <div className="flex-shrink-0">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Progress Bar */}
          <div className="mt-8">
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-primary to-primary/60 h-full transition-all duration-500 ease-out"
                style={{
                  width: `${(steps.filter(s => s.status === 'completed').length / steps.length) * 100}%`
                }}
              />
            </div>
            <p className="text-xs text-muted-foreground text-center mt-2">
              {Math.round((steps.filter(s => s.status === 'completed').length / steps.length) * 100)}% complete
            </p>
          </div>
        </div>

        {/* Fun fact or tip while waiting */}
        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground italic">
            This usually takes 30-60 seconds. Hang tight!
          </p>
        </div>
      </div>
    </div>
  );
};

export default GenerateVideo;
