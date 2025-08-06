"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Trophy, Coins, TrendingUp, Star, Gift, Zap, Target, Award } from "lucide-react"

interface LeaderboardEntry {
  username: string
  points: number
  rank: number
  change: number
  avatar: string
  streak: number
}

export default function RewardsPage() {
  const [aetherBalance, setAetherBalance] = useState(128.45)
  const [dailyStreak, setDailyStreak] = useState(7)
  const [nextReward, setNextReward] = useState(72)
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([
    { username: "@Speedster", points: 2847, rank: 1, change: 0, avatar: "🏎️", streak: 12 },
    { username: "@EcoRide", points: 2156, rank: 2, change: 2, avatar: "🌱", streak: 8 },
    { username: "@FastLane", points: 1923, rank: 3, change: -1, avatar: "⚡", streak: 15 },
    { username: "@GreenDriver", points: 1847, rank: 4, change: 1, avatar: "🍃", streak: 5 },
  ])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setAetherBalance((prev) => prev + Math.random() * 0.1)
      setNextReward((prev) => Math.max(0, prev - 1))
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const handleClaimRewards = () => {
    setAetherBalance((prev) => prev + 25.5)
    setNextReward(300) // Reset to 5 minutes
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Mobile Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800/50 text-xs">
        <div className="flex items-center gap-2">
          <span>24₵</span>
          <div className="w-1 h-1 bg-orange-400 rounded-full"></div>
        </div>
        <span className="font-mono">143:30</span>
        <div className="flex items-center gap-1">
          <Zap className="w-3 h-3 text-yellow-400" />
          <span>98%</span>
        </div>
      </div>

      {/* Mobile Header */}
      <header className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-600 to-amber-600">
        <Link href="/">
          <Button variant="ghost" size="sm" className="text-white hover:bg-orange-700/50">
            <ArrowLeft className="w-4 h-4" />
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <Trophy className="w-4 h-4 text-yellow-300" />
          <span className="text-sm font-medium">Rewards Center</span>
        </div>
      </header>

      <div className="p-4 max-w-sm mx-auto space-y-4">
        {/* Main Rewards Card */}
        <div className="bg-gradient-to-br from-orange-600 to-amber-600 rounded-2xl p-6 shadow-2xl">
          <h1 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Trophy className="w-6 h-6 text-yellow-300" />
            Rewards
          </h1>

          {/* AETHER Balance */}
          <Card className="bg-slate-800/80 border-slate-600/50 mb-4 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Coins className="w-4 h-4 text-amber-400" />
                  <span className="text-sm text-slate-400">AETHER Balance</span>
                </div>
                <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30">Live</Badge>
              </div>
              <div className="text-3xl font-bold text-white mb-2">{aetherBalance.toFixed(2)}</div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-3 h-3 text-green-400" />
                <span className="text-xs text-green-400">+12.5% this week</span>
              </div>
            </CardContent>
          </Card>

          {/* Daily Streak */}
          <Card className="bg-slate-800/80 border-slate-600/50 mb-4 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-yellow-400" />
                  <span className="text-sm text-slate-400">Daily Streak</span>
                </div>
                <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-300">
                  {dailyStreak} days
                </Badge>
              </div>
              <Progress value={(dailyStreak / 30) * 100} className="mb-2" />
              <span className="text-xs text-slate-400">{30 - dailyStreak} days to next milestone</span>
            </CardContent>
          </Card>

          {/* Claim Rewards Button */}
          <Button
            onClick={handleClaimRewards}
            className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 shadow-lg mb-4"
            disabled={nextReward > 0}
          >
            <Gift className="w-4 h-4 mr-2" />
            {nextReward > 0
              ? `Next reward in ${Math.floor(nextReward / 60)}:${(nextReward % 60).toString().padStart(2, "0")}`
              : "Claim Rewards"}
          </Button>

          {/* Leaderboard */}
          <Card className="bg-slate-800/80 border-slate-600/50 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Award className="w-4 h-4 text-orange-400" />
                <span className="text-orange-400 font-semibold text-sm">Leaderboard</span>
                <Badge variant="outline" className="ml-auto text-xs">
                  Weekly
                </Badge>
              </div>
              <div className="space-y-3">
                {leaderboard.map((entry, index) => (
                  <div key={entry.username} className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                          index === 0
                            ? "bg-gradient-to-r from-yellow-400 to-yellow-600 text-black"
                            : index === 1
                              ? "bg-gradient-to-r from-gray-300 to-gray-500 text-black"
                              : index === 2
                                ? "bg-gradient-to-r from-amber-600 to-amber-800 text-white"
                                : "bg-slate-600 text-white"
                        }`}
                      >
                        {entry.avatar}
                      </div>
                      <div>
                        <div className="text-sm text-white font-medium">{entry.username}</div>
                        <div className="text-xs text-slate-400 flex items-center gap-1">
                          <Target className="w-3 h-3" />
                          {entry.streak} day streak
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-orange-400 font-semibold text-sm">{entry.points.toLocaleString()}</div>
                      {entry.change !== 0 && (
                        <div
                          className={`flex items-center gap-1 justify-end ${
                            entry.change > 0 ? "text-green-400" : "text-red-400"
                          }`}
                        >
                          <TrendingUp className={`w-3 h-3 ${entry.change < 0 ? "rotate-180" : ""}`} />
                          <span className="text-xs">{Math.abs(entry.change)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Achievement Cards */}
        <div className="grid grid-cols-2 gap-3">
          <Card className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 border-purple-500/30">
            <CardContent className="p-3 text-center">
              <Trophy className="w-6 h-6 text-purple-400 mx-auto mb-1" />
              <div className="text-sm font-semibold text-purple-300">Top 10%</div>
              <div className="text-xs text-purple-400">This Month</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-green-600/20 to-green-800/20 border-green-500/30">
            <CardContent className="p-3 text-center">
              <Star className="w-6 h-6 text-green-400 mx-auto mb-1" />
              <div className="text-sm font-semibold text-green-300">Eco Hero</div>
              <div className="text-xs text-green-400">25% CO₂ Saved</div>
            </CardContent>
          </Card>
        </div>

        {/* Navigation Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <Link href="/home" className="flex-1">
            <Button
              variant="outline"
              className="w-full border-orange-600 text-orange-400 bg-transparent hover:bg-orange-600 hover:text-white"
            >
              Home
            </Button>
          </Link>
          <Link href="/trading" className="flex-1">
            <Button className="w-full bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700">
              Trading
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
