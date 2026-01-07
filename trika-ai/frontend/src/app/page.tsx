export default function LandingPage() {
    return (
        <div className="bg-black text-white overflow-x-hidden min-h-screen">
            {/* Particle Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-black to-cyan-900 opacity-60"></div>
                <div className="absolute inset-0 triangle-particles"></div>
            </div>

            {/* Hero */}
            <section className="relative min-h-screen flex items-center justify-center px-8">
                <div className="max-w-7xl mx-auto text-center">
                    {/* Logo */}
                    <div className="mb-16 animate-float">
                        <svg width="180" height="180" viewBox="0 0 200 200" className="mx-auto drop-shadow-2xl">
                            <path d="M100 20 L160 120 L40 120 Z" fill="none" stroke="#a78bfa" strokeWidth="3" opacity="0.8" />
                            <path d="M100 60 L130 115 L70 115 Z" fill="none" stroke="#c084fc" strokeWidth="3" opacity="0.9" />
                            <path d="M100 90 L115 120 L85 120 Z" fill="none" stroke="#e879f9" strokeWidth="3" />
                            <circle cx="100" cy="100" r="40" fill="none" stroke="#a78bfa" strokeWidth="2" opacity="0.4" />
                        </svg>
                    </div>

                    {/* Headline */}
                    <h1 className="text-6xl md:text-8xl lg:text-9xl font-machina font-extrabold tracking-tighter leading-none mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
                        Awaken Your<br />Infinite Self
                    </h1>

                    {/* Subheadline */}
                    <p className="text-xl md:text-2xl lg:text-3xl font-machina font-thin tracking-wide text-gray-300 max-w-4xl mx-auto mb-16 opacity-90">
                        The only platform that unites consciousness, capital & creation
                    </p>

                    {/* CTA */}
                    <div className="relative inline-block group">
                        <div className="absolute -inset-2 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full blur-xl opacity-70 group-hover:opacity-100 transition duration-1000 animate-pulseSlow"></div>
                        <a href="/chat" className="relative px-16 py-8 text-2xl md:text-3xl font-machina font-bold tracking-wider bg-white text-black rounded-full hover:scale-105 transition-all duration-500 shadow-2xl">
                            Begin the Ascension
                        </a>
                    </div>
                </div>
            </section>

            {/* Teaser Sections */}
            <section className="relative py-32 px-8">
                <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-12">
                    {['The Trinity Protocol', 'Conscious Creators', 'Spiritual Capital'].map((title, i) => (
                        <div key={i} className="backdrop-blur-xl bg-white/5 rounded-3xl p-12 border border-white/10 hover:border-white/30 transition-all duration-700 hover:scale-105">
                            <div className="text-5xl font-machina font-thin text-transparent bg-clip-text bg-gradient-to-br from-purple-400 to-cyan-400 mb-6">
                                0{i + 1}
                            </div>
                            <h3 className="text-4xl font-machina font-extrabold tracking-tight mb-4">{title}</h3>
                            <p className="text-gray-400 text-lg leading-relaxed">
                                {i === 0 && "Ancient wisdom encoded into unbreakable smart contracts"}
                                {i === 1 && "Where mystics, artists & visionaries monetize enlightenment"}
                                {i === 2 && "The new asset class: attention, energy, and awakened intention"}
                            </p>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
