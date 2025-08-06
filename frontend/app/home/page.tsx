"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Wifi, Battery, Signal, Share2, Clock, Trophy, TrendingUp } from "lucide-react"

interface Driver {
  username: string
  rank: number
  points: number
  change: number
}

export default function HomePage() {
  const [dataSharing, setDataSharing] = useState(true)
  const [lastUpload, setLastUpload] = useState(5)
  const [batteryLevel, setBatteryLevel] = useState(87)
  const [drivers, setDrivers] = useState<Driver[]>([
    { username: "@Speedster", rank: 1, points: 2847, change: 0 },
    { username: "@FastLane", rank: 2, points: 2156, change: 15 },
    { username: "@GreenDriver", rank: 3, points: 1923, change: 3 },
    { username: "@CityCommuter", rank: 4, points: 1847, change: 4 },
    { username: "@EcoRider", rank: 5, points: 1654, change: -2 },
  ])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpload((prev) => prev + 1)
      setBatteryLevel((prev) => Math.max(20, prev - Math.random() * 0.5))
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Mobile Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800/50 text-xs">
        <div className="flex items-center gap-1">
          <Signal className="w-3 h-3" />
          <Wifi className="w-3 h-3" />
        </div>
        <span className="font-mono">4:01</span>
        <div className="flex items-center gap-1">
          <span>{batteryLevel.toFixed(0)}%</span>
          <Battery className="w-3 h-3" />
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
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium">Connected</span>
        </div>
      </header>

      <div className="p-4 max-w-sm mx-auto space-y-4">
        {/* Main Control Card */}
        <div className="bg-gradient-to-br from-orange-600 to-amber-600 rounded-2xl p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-white">Home</h1>
            <div className="flex items-center gap-2">
              <Switch
                checked={dataSharing}
                onCheckedChange={setDataSharing}
                className="data-[state=checked]:bg-orange-800"
              />
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </div>

          {/* Data Sharing Status */}
          <Card className="bg-slate-800/80 border-slate-600/50 mb-4 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Share2 className="w-4 h-4 text-orange-400" />
                  <span className="text-orange-400 font-semibold text-sm">Opt-In Status</span>
                </div>
                <Badge variant={dataSharing ? "default" : "secondary"} className="text-xs">
                  {dataSharing ? "Active" : "Inactive"}
                </Badge>
              </div>
              <p className="text-orange-300 font-medium">Data Sharing</p>
              <Progress value={dataSharing ? 100 : 0} className="mt-2 h-1" />
            </CardContent>
          </Card>

          {/* Last Upload */}
          <Card className="bg-slate-800/80 border-slate-600/50 mb-4 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-slate-400" />
                <span className="text-sm text-slate-400">
                  Last Upload: <span className="text-xs text-slate-500">Live</span>
                </span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">{formatTime(lastUpload)} ago</div>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-1 h-1 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-400">Syncing...</span>
              </div>
            </CardContent>
          </Card>

          {/* Top Drivers Leaderboard */}
          <Card className="bg-slate-800/80 border-slate-600/50 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Trophy className="w-4 h-4 text-orange-400" />
                <span className="text-sm text-orange-400 font-semibold">
                  Top 5 <span className="text-xs text-orange-300">Drivers Today</span>
                </span>
              </div>
              <div className="space-y-3">
                {drivers.map((driver, index) => (
                  <div key={driver.username} className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                          index === 0
                            ? "bg-yellow-500 text-black"
                            : index === 1
                              ? "bg-gray-400 text-black"
                              : index === 2
                                ? "bg-amber-600 text-white"
                                : "bg-slate-600 text-white"
                        }`}
                      >
                        {driver.rank}
                      </div>
                      <span className="text-sm text-white">{driver.username}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-orange-400 font-semibold text-sm">{driver.points.toLocaleString()}</span>
                      {driver.change !== 0 && (
                        <div
                          className={`flex items-center gap-1 ${driver.change > 0 ? "text-green-400" : "text-red-400"}`}
                        >
                          <TrendingUp className={`w-3 h-3 ${driver.change < 0 ? "rotate-180" : ""}`} />
                          <span className="text-xs">{Math.abs(driver.change)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Navigation Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <Link href="/rewards" className="flex-1">
            <Button className="w-full bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 shadow-lg">
              <Trophy className="w-4 h-4 mr-2" />
              Rewards
            </Button>
          </Link>
          <Link href="/trading" className="flex-1">
            <Button
              variant="outline"
              className="w-full border-orange-600 text-orange-400 bg-transparent hover:bg-orange-600 hover:text-white shadow-lg"
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Trading
            </Button>
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-2 mt-4">
          <Card className="bg-slate-800/50 border-slate-600/50">
            <CardContent className="p-3 text-center">
              <div className="text-lg font-bold text-teal-400">87%</div>
              <div className="text-xs text-slate-400">Efficiency</div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-600/50">
            <CardContent className="p-3 text-center">
              <div className="text-lg font-bold text-green-400">24.5</div>
              <div className="text-xs text-slate-400">CO₂ Saved</div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-600/50">
            <CardContent className="p-3 text-center">
              <div className="text-lg font-bold text-orange-400">1.2k</div>
              <div className="text-xs text-slate-400">Points</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
