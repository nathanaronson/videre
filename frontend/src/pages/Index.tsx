import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Sparkles, Zap, Brain, Video, Search, TrendingUp } from 'lucide-react';
import GeometricBackground from '@/components/GeometricBackground';
import FeatureCard from '@/components/FeatureCard';
import { toast } from 'sonner';
const Index = () => {
  const [topic, setTopic] = useState('');
  const handleGenerate = () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic to learn about');
      return;
    }
    toast.success(`Generating video about: ${topic}`);
    // Video generation logic would go here
  };
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleGenerate();
    }
  };
  return <div className="min-h-screen bg-background relative">
      <GeometricBackground />
      
      {/* Hero Section */}
      <section className="relative container mx-auto px-4 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50 border border-border/50 mb-8 backdrop-blur-sm">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-foreground">AI-Powered Learning</span>
          </div>
          
          {/* Main Heading */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Master Math & CS with{' '}
            <span className="text-gradient">AI-Generated Videos</span>
          </h1>
          
          <p className="text-muted-foreground mb-12 max-w-2xl mx-auto text-lg">Transform complex math and computer science concepts into clear, visual explanations, in one click</p>
          
          {/* Search Input */}
          <div className="max-w-2xl mx-auto mb-8">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-primary rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300" />
              <div className="relative flex gap-3 p-10 rounded-2xl border border-border/50 backdrop-blur-sm shadow-elevated bg-sky-800">
                <div className="flex-1 flex items-center gap-2 px-4">
                  <Search className="w-5 h-5 text-muted-foreground" />
                  <Input type="text" placeholder="Enter a math or CS topic... (e.g., differential equations, quicksort, graph theory)" value={topic} onChange={e => setTopic(e.target.value)} onKeyPress={handleKeyPress} className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base" />
                </div>
                <Button variant="hero" size="lg" onClick={handleGenerate} className="px-8">
                  <Video className="w-5 h-5" />
                  Generate Video
                </Button>
              </div>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span>Instant Generation</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-secondary animate-pulse" style={{
              animationDelay: '0.5s'
            }} />
              <span>​High Quality Graphics</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" style={{
              animationDelay: '1s'
            }} />
              <span>Educational Excellence
            </span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative container mx-auto px-4 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why Choose <span className="text-gradient">​Videre</span>?
            </h2>
            <p className="text-muted-foreground text-lg">
              Experience the future of learning with cutting-edge AI technology
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard icon={<Zap className="w-8 h-8" />} title="Complex Concepts, Simply Explained" description="Transform abstract mathematical proofs and algorithms into visual, intuitive explanations you can actually understand." />
            <FeatureCard icon={<Brain className="w-8 h-8" />} title="Step-by-Step Breakdowns" description="Watch equations solve themselves, algorithms execute in real-time, and theorems build piece by piece." />
            <FeatureCard icon={<Video className="w-8 h-8" />} title="Visual Proofs & Animations" description="See calculus limits converge, sorting algorithms in action, and data structures come to life through animation." />
            <FeatureCard icon={<TrendingUp className="w-8 h-8" />} title="From Basics to Advanced" description="Whether you're learning basic algebra or tackling computational complexity theory, content scales with you." />
            <FeatureCard icon={<Sparkles className="w-8 h-8" />} title="Complete Math & CS Coverage" description="Calculus, linear algebra, discrete math, algorithms, data structures, theory of computation, and beyond." />
            <FeatureCard icon={<Search className="w-8 h-8" />} title="Academically Rigorous" description="Every explanation grounded in mathematical accuracy and computer science fundamentals." />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-card border border-border/50 p-12 text-center backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Ready to Master Math & CS?
              </h2>
              <p className="text-muted-foreground text-lg mb-8 max-w-2xl mx-auto">
                Join students and professionals learning mathematics and computer science through AI-powered visual explanations
              </p>
              <Button variant="hero" size="lg" onClick={() => window.scrollTo({
              top: 0,
              behavior: 'smooth'
            })}>
                <Sparkles className="w-5 h-5" />
                Start Creating Videos
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-border/50 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2024 LearnAI. Making mathematics and computer science accessible through AI.</p>
        </div>
      </footer>
    </div>;
};
export default Index;