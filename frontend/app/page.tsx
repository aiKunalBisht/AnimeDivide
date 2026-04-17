import Link from "next/link";
import { getShows } from "@/lib/api";

export const revalidate = 0; // Opt out of static caching to ensure fresh API data

function getScoreColorClass(divide: number | undefined) {
  if (divide === undefined) return "text-gray-400";
  const absDivide = Math.abs(divide);
  if (absDivide > 0.3) return "text-red-500";
  if (absDivide > 0.1) return "text-yellow-500";
  return "text-green-500";
}

export default async function HomePage() {
  const shows = await getShows();
  
  const topShows = shows.slice(0, 3);
  const remainingShows = shows.slice(3);

  return (
    <main className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-7xl mx-auto space-y-16 py-8">
        
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 leading-tight">
            Anime Fandom Divide
          </h1>
          <p className="text-xl md:text-2xl font-medium text-gray-400 max-w-3xl mx-auto leading-relaxed">
            Exploring the contrast in sentiment between Japanese and English speaking communities across popular anime series.
          </p>
        </div>

        {/* Top 3 Shows */}
        {topShows.length > 0 && (
          <div className="space-y-8">
            <h2 className="text-3xl font-bold flex items-center gap-3">
              <span className="text-red-500 text-4xl">🔥</span> Most Polarizing Series
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {topShows.map((show) => (
                <Link key={show.slug} href={`/shows/${show.slug}`} className="block group relative bg-gray-900 border border-gray-800 rounded-3xl p-8 hover:bg-gray-800 transition-all duration-300 transform hover:-translate-y-2 hover:shadow-2xl hover:shadow-red-500/10">
                  <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-red-500 to-transparent rounded-t-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  
                  <h3 className="text-3xl font-black text-gray-100 mb-2 truncate group-hover:text-red-400 transition-colors">{show.title_en}</h3>
                  <div className="text-sm font-medium text-gray-500 mb-8 flex justify-between items-center">
                    <span className="truncate mr-4">{show.title_jp}</span>
                    <span className="bg-gray-800 px-3 py-1 rounded text-xs tracking-widest">{show.year}</span>
                  </div>
                  
                  {show.top_divide ? (
                    <div className="flex justify-between items-end bg-black/40 p-5 rounded-2xl border border-gray-800/50">
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-widest mb-1.5 font-semibold">Top Divided Topic</p>
                        <p className="text-xl font-bold capitalize text-gray-200">{show.top_divide.topic}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500 uppercase tracking-widest mb-1.5 font-semibold">Divide Score</p>
                        <p className={`text-5xl font-black tracking-tighter ${getScoreColorClass(show.top_divide.divide)}`}>
                          {Math.abs(show.top_divide.divide).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="pt-10 text-center text-gray-500">No scoring data available.</div>
                  )}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Remaining Shows Grid */}
        {remainingShows.length > 0 && (
          <div className="space-y-8 pt-10 border-t border-gray-800/80">
            <h2 className="text-2xl font-bold text-gray-200 flex items-center gap-3">
              <span className="text-blue-500 text-3xl">📚</span> All Other Series
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {remainingShows.map((show) => (
                <Link key={show.slug} href={`/shows/${show.slug}`} className="bg-gray-900 border border-gray-800 rounded-2xl p-6 hover:bg-gray-800 hover:border-gray-700 transition-all duration-200 group">
                  <h3 className="text-xl font-bold text-gray-100 truncate mb-1 group-hover:text-blue-400 transition-colors">{show.title_en}</h3>
                  <div className="flex justify-between items-center text-xs font-semibold text-gray-500 mb-6">
                    <span className="bg-gray-800 px-2.5 py-1 rounded-md">{show.year}</span>
                    {show.top_divide && <span className="text-gray-400 capitalize">{show.top_divide.topic}</span>}
                  </div>
                  
                  {show.top_divide ? (
                     <div className="flex justify-between items-center bg-black/60 rounded-xl p-4">
                       <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Abs Divide</span>
                       <span className={`text-2xl font-black ${getScoreColorClass(show.top_divide.divide)}`}>
                         {Math.abs(show.top_divide.divide).toFixed(2)}
                       </span>
                     </div>
                  ) : (
                    <div className="text-sm text-gray-600 bg-black/60 rounded-xl p-4 text-center font-semibold">Data Unavailable</div>
                  )}
                </Link>
              ))}
            </div>
          </div>
        )}

      </div>
    </main>
  );
}
