"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { NetworkVisualization } from "@/components/network-visualization"
import { TrafficMetrics } from "@/components/traffic-metrics"
import { RealtimeChart } from "@/components/realtime-chart"
import { Navigation } from "@/components/navigation"
import { StatusIndicator } from "@/components/status-indicator"
import { MetricCard } from "@/components/metric-card"
import { SystemHealth } from "@/components/system-health"
import { AlertsPanel } from "@/components/alerts-panel"
import { useToast } from "@/hooks/use-toast"
import { Activity, Car, Leaf, Settings, Users, TrendingUp, MapPin, Clock, Zap, Shield, Globe, Database, Cpu, Wifi, Bell } from 'lucide-react'

interface TrafficData {
  timestamp: number
  vehicles: number
  co2Saved: number
  optInRate: number
  congestionLevel: "low" | "medium" | "high"
  activeIntersections: number
  networkLatency: number
  systemLoad: number
}

export default function Dashboard() {
  const [trafficData, setTrafficData] = useState<TrafficData>({
    timestamp: Date.now(),
    vehicles: 1482,
    co2Saved: 24.7,
    optInRate: 87.3,
    congestionLevel: "medium",
    activeIntersections: 14,
    networkLatency: 12,
    systemLoad: 68,
  })

  const [selectedIntersection, setSelectedIntersection] = useState("intersection14")
  const [isOptimizing, setIsOptimizing] = useState(true)
  const [systemStatus, setSystemStatus] = useState<"active" | "maintenance" | "offline">("active")
  const [currentTime, setCurrentTime] = useState(new Date())
  const { toast } = useToast()

  // Real-time data simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setTrafficData((prev) => ({
        ...prev,
        timestamp: Date.now(),
        vehicles: Math.max(800, prev.vehicles + Math.floor(Math.random() * 40 - 20)),
        co2Saved: Math.max(0, prev.co2Saved + (Math.random() - 0.5) * 1.5),
        optInRate: Math.max(70, Math.min(95, prev.optInRate + (Math.random() - 0.5) * 3)),
        networkLatency: Math.max(5, Math.min(50, prev.networkLatency + (Math.random() - 0.5) * 5)),
        systemLoad: Math.max(30, Math.min(90, prev.systemLoad + (Math.random() - 0.5) * 8)),
      }))
      setCurrentTime(new Date())
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const handleSaveChanges = () => {
    toast({
      title: "Configuration Updated",
      description: "Traffic optimization parameters have been successfully applied to all intersections.",
    })
  }

  const handleOptimizationToggle = (enabled: boolean) => {
    setIsOptimizing(enabled)
    toast({
      title: enabled ? "AI Optimization Activated" : "Manual Mode Enabled",
      description: enabled
        ? "Advanced machine learning algorithms are now managing traffic flow optimization."
        : "System switched to manual control mode. All automated optimizations paused.",
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Professional Header */}
      <header className="border-b border-slate-800/50 bg-slate-900/95 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center justify-between px-8 py-4">
          <div className="flex items-center gap-6">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 via-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/25">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-slate-900 animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                Aetherflow
              </h1>
              <p className="text-sm text-slate-400 font-medium">Enterprise Traffic Intelligence Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-4 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <Globe className="w-4 h-4 text-emerald-400" />
              <span className="text-sm text-slate-300 font-mono">{currentTime.toLocaleTimeString()}</span>
              <Separator orientation="vertical" className="h-4" />
              <span className="text-sm text-slate-400">UTC-5</span>
            </div>
            
            <SystemHealth 
              latency={trafficData.networkLatency}
              systemLoad={trafficData.systemLoad}
              status={systemStatus}
            />

            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
                <Users className="w-4 h-4 text-white" />
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-slate-200">Admin Console</div>
                <div className="text-xs text-slate-400">System Administrator</div>
              </div>
            </div>

            <Select defaultValue="en">
              <SelectTrigger className="w-24 bg-slate-800/50 border-slate-700/50 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">EN</SelectItem>
                <SelectItem value="es">ES</SelectItem>
                <SelectItem value="fr">FR</SelectItem>
                <SelectItem value="de">DE</SelectItem>
                <SelectItem value="zh">中文</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </header>

      <div className="p-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4 py-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-orange-300 via-amber-300 to-orange-400 bg-clip-text text-transparent">
            Real-Time Traffic Intelligence Dashboard
          </h1>
          <p className="text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed">
            Advanced AI-powered traffic optimization with predictive analytics, environmental impact tracking, and blockchain-based incentive systems
          </p>
          <div className="flex items-center justify-center gap-4 pt-4">
            <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 px-3 py-1">
              <Activity className="w-3 h-3 mr-1" />
              Live System
            </Badge>
            <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 px-3 py-1">
              <Shield className="w-3 h-3 mr-1" />
              Enterprise Grade
            </Badge>
            <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 px-3 py-1">
              <Database className="w-3 h-3 mr-1" />
              Real-time Analytics
            </Badge>
          </div>
        </div>

        {/* Enhanced Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Network Participation"
            value={trafficData.optInRate}
            unit="%"
            change={+2.3}
            icon={Users}
            description="Active data sharing participants"
            color="teal"
            trend="up"
          />
          
          <MetricCard
            title="Environmental Impact"
            value={trafficData.co2Saved}
            unit="% CO₂ Reduced"
            change={+1.8}
            icon={Leaf}
            description="Carbon emissions prevented"
            color="emerald"
            trend="up"
          />
          
          <MetricCard
            title="Active Fleet"
            value={trafficData.vehicles}
            unit="vehicles"
            change={+5.2}
            icon={Car}
            description="Real-time tracked vehicles"
            color="blue"
            trend="up"
          />
          
          <MetricCard
            title="Network Nodes"
            value={trafficData.activeIntersections}
            unit="intersections"
            change={0}
            icon={MapPin}
            description="Managed traffic intersections"
            color="purple"
            trend="stable"
          />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Network Visualization - Takes 2 columns */}
          <div className="xl:col-span-2 space-y-6">
            <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">
                      <Activity className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <div className="text-xl font-semibold text-slate-100">Network Traffic Flow</div>
                      <div className="text-sm text-slate-400">Real-time traffic pattern analysis</div>
                    </div>
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-slate-400 font-mono">Live</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <NetworkVisualization data={trafficData} />
              </CardContent>
            </Card>

            <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-xl font-semibold text-slate-100">Performance Analytics</div>
                    <div className="text-sm text-slate-400">Multi-dimensional traffic metrics</div>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <RealtimeChart />
              </CardContent>
            </Card>
          </div>

          {/* Control Panel - Takes 1 column */}
          <div className="space-y-6">
            <Card className="bg-gradient-to-br from-orange-900/30 via-amber-900/20 to-orange-900/30 border-orange-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-orange-100 flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-orange-400" />
                  System Control Center
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center">
                      <Zap className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <div className="font-medium text-orange-100">AI Optimization Engine</div>
                      <div className="text-sm text-orange-300">Machine learning traffic control</div>
                    </div>
                  </div>
                  <Switch 
                    checked={isOptimizing} 
                    onCheckedChange={handleOptimizationToggle}
                    className="data-[state=checked]:bg-emerald-600"
                  />
                </div>

                <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-orange-200 font-medium">System Status</span>
                    <StatusIndicator status={systemStatus} />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Network Latency</span>
                      <span className="text-slate-200 font-mono">{trafficData.networkLatency}ms</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">System Load</span>
                      <span className="text-slate-200 font-mono">{trafficData.systemLoad}%</span>
                    </div>
                    <Progress value={trafficData.systemLoad} className="h-2 mt-2" />
                  </div>
                </div>

                <Button 
                  className="w-full bg-gradient-to-r from-orange-600 via-amber-600 to-orange-600 hover:from-orange-700 hover:via-amber-700 hover:to-orange-700 shadow-lg shadow-orange-500/25 text-white font-semibold"
                  size="lg"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Claim Network Rewards
                </Button>
              </CardContent>
            </Card>

            <TrafficMetrics />
            <AlertsPanel />
          </div>
        </div>

        {/* Advanced Traffic Control Center */}
        <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-violet-500 rounded-lg flex items-center justify-center">
                  <Settings className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className="text-xl font-semibold text-slate-100">Traffic Control Center</div>
                  <div className="text-sm text-slate-400">Advanced intersection management system</div>
                </div>
              </CardTitle>
              <div className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-amber-400" />
                <span className="text-sm text-amber-400 font-medium">3 Active Alerts</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
              <Select value={selectedIntersection} onValueChange={setSelectedIntersection}>
                <SelectTrigger className="bg-slate-800/50 border-slate-700/50">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="intersection14">Intersection 14 - Main & 5th</SelectItem>
                  <SelectItem value="intersection15">Intersection 15 - Broadway & Oak</SelectItem>
                  <SelectItem value="intersection16">Intersection 16 - Central & Pine</SelectItem>
                  <SelectItem value="intersection17">Intersection 17 - Market & 1st</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <div>
                  <div className="text-sm font-medium text-slate-200">Status</div>
                  <div className="text-xs text-red-400">High Congestion</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <Clock className="w-4 h-4 text-slate-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Time</div>
                  <div className="text-xs text-slate-400 font-mono">{currentTime.toLocaleTimeString()}</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <Wifi className="w-4 h-4 text-emerald-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Connection</div>
                  <div className="text-xs text-emerald-400">Online</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <Activity className="w-4 h-4 text-blue-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Flow Rate</div>
                  <div className="text-xs text-blue-400 font-mono">847 veh/hr</div>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <Button
                onClick={handleSaveChanges}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-semibold shadow-lg shadow-emerald-500/25"
              >
                <Settings className="w-4 h-4 mr-2" />
                Apply Configuration
              </Button>
              <Button 
                variant="outline" 
                className="border-slate-600 text-slate-300 hover:bg-slate-800 bg-slate-900/50 backdrop-blur-sm"
              >
                Reset to Defaults
              </Button>
              <Button 
                variant="outline" 
                className="border-amber-600 text-amber-400 hover:bg-amber-600 hover:text-white bg-slate-900/50 backdrop-blur-sm"
              >
                <Bell className="w-4 h-4 mr-2" />
                Emergency Override
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Navigation */}
        <Navigation />
      </div>
    </div>
  )
}
