"use client"

import { useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, BarChart3, TrendingUp, TrendingDown, Car, Leaf, MapPin } from "lucide-react"

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("24h")
  const [selectedMetric, setSelectedMetric] = useState("traffic")

  const metrics = {
    traffic: {
      current: 1482,
      change: 12.5,
      trend: "up",
      unit: "vehicles",
    },
    efficiency: {
      current: 87.3,
      change: -2.1,
      trend: "down",
      unit: "%",
    },
    co2Saved: {
      current: 24.7,
      change: 8.9,
      trend: "up",
      unit: "%",
    },
    responseTime: {
      current: 1.2,
      change: -15.3,
      trend: "up",
      unit: "s",
    },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Header */}
      <header className="flex items-center justify-between p-4 bg-slate-800/50 border-b border-slate-700">
        <Link href="/">
          <Button variant="ghost" size="sm" className="text-white hover:bg-slate-700">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-orange-400" />
          <span className="font-semibold">Analytics Center</span>
        </div>
      </header>

      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-300 to-amber-300 bg-clip-text text-transparent">
            Traffic Analytics Dashboard
          </h1>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32 bg-slate-800 border-slate-600">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1h">Last Hour</SelectItem>
              <SelectItem value="24h">Last 24h</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Key Performance Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Object.entries(metrics).map(([key, metric]) => (
            <Card key={key} className="bg-slate-800/50 border-slate-600/50 hover:border-slate-500/50 transition-all">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="capitalize text-slate-400 text-sm font-medium">{key.replace(/([A-Z])/g, " $1")}</div>
                  <Badge
                    className={metric.trend === "up" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}
                  >
                    {metric.trend === "up" ? (
                      <TrendingUp className="w-3 h-3 mr-1" />
                    ) : (
                      <TrendingDown className="w-3 h-3 mr-1" />
                    )}
                    {Math.abs(metric.change)}%
                  </Badge>
                </div>
                <div className="text-2xl font-bold text-white mb-1">
                  {metric.current}
                  {metric.unit}
                </div>
                <div className="text-xs text-slate-400">vs. previous period</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Detailed Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-slate-800/50 border-slate-600/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Car className="w-5 h-5 text-blue-400" />
                Vehicle Flow Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-400">Peak Hours</span>
                  <span className="text-white font-semibold">8-10 AM, 5-7 PM</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-400">Average Speed</span>
                  <span className="text-white font-semibold">45.2 km/h</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-400">Congestion Index</span>
                  <div className="flex items-center gap-2">
                    <Progress value={65} className="w-20 h-2" />
                    <span className="text-white font-semibold">65%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-600/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Leaf className="w-5 h-5 text-green-400" />
                Environmental Impact
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-400">CO₂ Reduction</span>
                  <span className="text-green-400 font-semibold">24.7%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-400">Fuel Saved</span>
                  <span className="text-green-400 font-semibold">1,247 L</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-400">Trees Equivalent</span>
                  <span className="text-green-400 font-semibold">156 trees</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Intersection Performance */}
        <Card className="bg-slate-800/50 border-slate-600/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-orange-400" />
              Intersection Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { id: "INT-14", efficiency: 92, status: "optimal", vehicles: 847 },
                { id: "INT-15", efficiency: 78, status: "congested", vehicles: 1203 },
                { id: "INT-16", efficiency: 85, status: "active", vehicles: 692 },
              ].map((intersection) => (
                <div key={intersection.id} className="p-4 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-semibold text-white">{intersection.id}</span>
                    <Badge
                      className={
                        intersection.status === "optimal"
                          ? "bg-green-500/20 text-green-400"
                          : intersection.status === "congested"
                            ? "bg-red-500/20 text-red-400"
                            : "bg-blue-500/20 text-blue-400"
                      }
                    >
                      {intersection.status}
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Efficiency</span>
                      <span className="text-white">{intersection.efficiency}%</span>
                    </div>
                    <Progress value={intersection.efficiency} className="h-2" />
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Vehicles/hr</span>
                      <span className="text-white">{intersection.vehicles}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
