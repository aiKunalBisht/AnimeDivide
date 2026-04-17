import Link from "next/link";
import { getShow, getNarrative } from "@/lib/api";
import RadarChart from "@/components/RadarChart";

export const revalidate = 0; // Ensure fresh data from backend

export default async function ShowPage({ params }: { params: { slug: string } }) {
  const show = await getShow(params.slug);
  const narrative = await getNarrative(params.slug);

  const chartData = show.topics.map(t => ({
    topic: t.topic.charAt(0).toUpperCase() + t.topic.slice(1),
    jp_score: Number(t.jp_score.toFixed(2)),
    en_score: Number(t.en_score.toFixed(2)),
  }));

  const avgJp = chartData.length ? chartData.reduce((a, b) => a + b.jp_score, 0) / chartData.length : 0;
  const avgEn = chartData.length ? chartData.reduce((a, b) => a + b.en_score, 0) / chartData.length : 0;

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6 md:p-14">
      <div className="max-w-6xl mx-auto space-y-12">
        
        <Link href="/" className="inline-flex items-center text-sm font-bold text-gray-500 hover:text-white transition-colors group tracking-widest uppercase">
          <span className="mr-3 transform group-hover:-translate-x-2 transition-transform">←</span>
          Back
        </Link>
        
        <div className="space-y-3 border-b border-gray-800/80 pb-10">
          <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white mb-2">{show.title_en}</h1>
          <h2 className="text-2xl text-gray-400 font-medium tracking-wide">{show.title_jp}</h2>
          
          <div className="flex flex-wrap gap-4 pt-6 text-sm font-bold tracking-widest">
            <div className="bg-gray-900 border border-gray-800 rounded-xl px-4 py-2 flex items-center">
              <span className="text-gray-600 mr-3">YEAR</span>
              <span className="text-gray-100">{show.year}</span>
            </div>
            <div className="bg-blue-950/30 border border-blue-900/50 rounded-xl px-4 py-2 flex items-center">
              <span className="text-blue-500/70 mr-3">EN REVIEWS</span>
              <span className="text-blue-400">{show.post_count?.en || 0}</span>
            </div>
            <div className="bg-red-950/30 border border-red-900/50 rounded-xl px-4 py-2 flex items-center">
              <span className="text-red-500/70 mr-3">JP REVIEWS</span>
              <span className="text-red-400">{show.post_count?.jp || 0}</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Chart Section */}
          <div className="bg-gray-900/40 rounded-[2.5rem] p-8 border border-gray-800/60 shadow-2xl relative">
            <div className="absolute top-8 left-8">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest flex items-center">
                <span className="w-2 h-2 rounded-full bg-blue-500 mr-3 shadow-[0_0_10px_rgba(59,130,246,0.8)]"></span>
                Sentiment Distribution
              </h3>
            </div>
            <div className="mt-12">
              <RadarChart data={chartData} />
            </div>
          </div>

          {/* Context Section */}
          <div className="space-y-8">
            <div className="bg-gradient-to-br from-gray-900 to-black rounded-[2.5rem] p-10 border border-gray-800 relative overflow-hidden group shadow-2xl">
              <div className="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-red-500 to-blue-500 shadow-[0_0_20px_rgba(239,68,68,0.5)]"></div>
              <div className="absolute -inset-1 bg-gradient-to-r from-red-500/5 to-blue-500/5 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
              
              <h3 className="text-xs font-black text-gray-600 uppercase tracking-widest mb-6">AI Architecture Narrative</h3>
              <blockquote className="text-2xl leading-relaxed font-light text-gray-300 italic relative z-10">
                "{narrative}"
              </blockquote>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gray-900/50 rounded-3xl p-8 border border-gray-800/80">
                 <p className="text-xs font-black text-red-500/80 uppercase tracking-widest mb-3">JP Aggregate</p>
                 <p className="text-4xl font-black text-white">
                   {avgJp > 0 ? "+" : ""}{avgJp.toFixed(2)}
                 </p>
              </div>
              <div className="bg-gray-900/50 rounded-3xl p-8 border border-gray-800/80">
                 <p className="text-xs font-black text-blue-500/80 uppercase tracking-widest mb-3">EN Aggregate</p>
                 <p className="text-4xl font-black text-white">
                   {avgEn > 0 ? "+" : ""}{avgEn.toFixed(2)}
                 </p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </main>
  );
}
