import React, { useState, useEffect } from 'react';
import { MapPin, Calendar, Activity, Plus, Flame, Eye } from 'lucide-react';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [analyzing, setAnalyzing] = useState({}); // Tracks which cards are in "Predator Mode"
  const [showAddModal, setShowAddModal] = useState(false);
  const [newLoc, setNewLoc] = useState({ name: '', lat: '', lon: '' });

  useEffect(() => {
    fetch('/satellite_data.json')
      .then(res => res.json())
      .then(setData);
  }, []);

  // Toggle between Visual and Thermal
  const toggleAnalysis = (id) => {
    setAnalyzing(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Construct the GitHub Issue URL
  const handleAddLocation = () => {
    const issueTitle = `ADD_TARGET: ${newLoc.name}`;
    const issueBody = JSON.stringify({
      id: newLoc.name.toLowerCase().replace(/\s/g, '_'),
      name: newLoc.name,
      lat: parseFloat(newLoc.lat),
      lon: parseFloat(newLoc.lon),
      zoom: 0.1
    }, null, 2);

    // Replace with YOUR actual Repo URL
    const repoUrl = "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/issues/new"; 
    window.open(`${repoUrl}?title=${encodeURIComponent(issueTitle)}&body=${encodeURIComponent(issueBody)}`, '_blank');
    setShowAddModal(false);
  };

  if (!data) return <div className="flex h-screen items-center justify-center bg-gray-900 text-green-500 font-mono">INITIALIZING SATELLITE UPLINK...</div>;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans p-8">
      {/* Header */}
      <header className="mb-12 flex justify-between items-center max-w-6xl mx-auto border-b border-gray-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Orbital Command</h1>
          <p className="text-gray-400 mt-1 flex items-center gap-2 text-sm">
            <Activity size={14} className="text-green-500 animate-pulse" />
            LIVE FEED • {data.last_updated}
          </p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} /> Add Target
        </button>
      </header>

      {/* Grid */}
      <main className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {data.locations.map((loc) => {
          const isThermal = analyzing[loc.id];
          return (
            <div key={loc.id} className="bg-gray-900 rounded-xl overflow-hidden border border-gray-800 hover:border-green-500/50 transition-all group">
              
              {/* Image View */}
              <div className="relative h-64 bg-black">
                <img 
                  src={isThermal ? loc.image_thermal : loc.image_visual} 
                  alt={loc.name} 
                  className={`w-full h-full object-cover transition-opacity duration-500 ${isThermal ? 'opacity-90 hue-rotate-180 invert' : 'opacity-100'}`}
                />
                
                {/* Status Badge */}
                <div className="absolute top-4 left-4 flex gap-2">
                  <span className={`text-[10px] font-bold px-2 py-1 rounded border ${isThermal ? 'bg-red-900/80 border-red-500 text-red-200' : 'bg-black/50 border-white/20 text-white'}`}>
                    {isThermal ? 'THERMAL // ANOMALY SCAN' : 'OPTICAL // RGB'}
                  </span>
                </div>
              </div>

              {/* Controls */}
              <div className="p-5">
                <h2 className="text-xl font-bold text-white mb-1">{loc.name}</h2>
                <div className="flex items-center gap-2 text-xs text-gray-400 mb-4 font-mono">
                  <MapPin size={12} /> {loc.coordinates}
                </div>

                <button 
                  onClick={() => toggleAnalysis(loc.id)}
                  className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all ${
                    isThermal 
                    ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/50' 
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {isThermal ? <><Eye size={16}/> Return to Optical</> : <><Flame size={16}/> Analyze Sector</>}
                </button>
              </div>
            </div>
          );
        })}
      </main>

      {/* Add Location Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-gray-900 border border-gray-700 p-6 rounded-xl w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Request New Satellite Target</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 uppercase font-bold">Target Name</label>
                <input 
                  className="w-full bg-gray-800 border border-gray-700 text-white p-2 rounded mt-1 focus:outline-none focus:border-green-500"
                  placeholder="e.g. Area 51"
                  onChange={e => setNewLoc({...newLoc, name: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-gray-400 uppercase font-bold">Latitude</label>
                  <input 
                    className="w-full bg-gray-800 border border-gray-700 text-white p-2 rounded mt-1"
                    placeholder="37.23"
                    onChange={e => setNewLoc({...newLoc, lat: e.target.value})}
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-400 uppercase font-bold">Longitude</label>
                  <input 
                    className="w-full bg-gray-800 border border-gray-700 text-white p-2 rounded mt-1"
                    placeholder="-115.80"
                    onChange={e => setNewLoc({...newLoc, lon: e.target.value})}
                  />
                </div>
              </div>
              <button 
                onClick={handleAddLocation}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-bold mt-2"
              >
                Initialize Request
              </button>
              <button onClick={() => setShowAddModal(false)} className="w-full text-gray-500 text-sm py-2">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
