"use client"

import { useEffect, useRef, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface NetworkNode {
  id: string
  x: number
  y: number
  type: "intersection" | "vehicle" | "sensor" | "hub"
  status: "optimal" | "congested" | "warning" | "offline"
  connections: string[]
  traffic: number
  name: string
}

interface NetworkVisualizationProps {
  data: {
    vehicles: number
    congestionLevel: "low" | "medium" | "high"
    activeIntersections: number
  }
}

export function NetworkVisualization({ data }: NetworkVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [nodes, setNodes] = useState<NetworkNode[]>([])
  const [animationFrame, setAnimationFrame] = useState(0)
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null)

  useEffect(() => {
    const initialNodes: NetworkNode[] = [
      { 
        id: "hub1", 
        x: 200, 
        y: 150, 
        type: "hub", 
        status: "optimal", 
        connections: ["int1", "int2", "int3"], 
        traffic: 95,
        name: "Central Hub"
      },
      { 
        id: "int1", 
        x: 120, 
        y: 80, 
        type: "intersection", 
        status: "optimal", 
        connections: ["hub1", "int2"], 
        traffic: 78,
        name: "Main & 5th"
      },
      { 
        id: "int2", 
        x: 280, 
        y: 100, 
        type: "intersection", 
        status: "congested", 
        connections: ["hub1", "int1", "int3"], 
        traffic: 142,
        name: "Broadway & Oak"
      },
      { 
        id: "int3", 
        x: 160, 
        y: 220, 
        type: "intersection", 
        status: "warning", 
        connections: ["hub1", "int2"], 
        traffic: 89,
        name: "Central & Pine"
      },
      { 
        id: "sensor1", 
        x: 80, 
        y: 180, 
        type: "sensor", 
        status: "optimal", 
        connections: [], 
        traffic: 0,
        name: "Traffic Sensor A1"
      },
      { 
        id: "sensor2", 
        x: 320, 
        y: 180, 
        type: "sensor", 
        status: "optimal", 
        connections: [], 
        traffic: 0,
        name: "Traffic Sensor B2"
      },
    ]
    setNodes(initialNodes)
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw grid background
      ctx.strokeStyle = "#1e293b"
      ctx.lineWidth = 1
      for (let x = 0; x < canvas.width; x += 40) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
      }
      for (let y = 0; y < canvas.height; y += 40) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(canvas.width, y)
        ctx.stroke()
      }

      // Draw connections with animated data flow
      nodes.forEach((node) => {
        node.connections.forEach((connectionId) => {
          const connectedNode = nodes.find((n) => n.id === connectionId)
          if (connectedNode) {
            // Base connection line
            ctx.beginPath()
            ctx.moveTo(node.x, node.y)
            ctx.lineTo(connectedNode.x, connectedNode.y)
            ctx.strokeStyle = "#475569"
            ctx.lineWidth = 2
            ctx.stroke()

            // Animated data flow
            const distance = Math.sqrt(
              Math.pow(connectedNode.x - node.x, 2) + Math.pow(connectedNode.y - node.y, 2)
            )
            const progress = (animationFrame * 0.02) % 1
            const flowX = node.x + (connectedNode.x - node.x) * progress
            const flowY = node.y + (connectedNode.y - node.y) * progress

            ctx.beginPath()
            ctx.arc(flowX, flowY, 3, 0, 2 * Math.PI)
            ctx.fillStyle = "#f97316"
            ctx.fill()
          }
        })
      })

      // Draw traffic flow paths
      const time = animationFrame * 0.03
      
      // Primary traffic flow
      ctx.beginPath()
      ctx.strokeStyle = "#f97316"
      ctx.lineWidth = 4
      ctx.globalAlpha = 0.8
      for (let x = 20; x <= 380; x += 2) {
        const y = 120 + Math.sin((x + time * 100) * 0.02) * 20
        if (x === 20) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }
      ctx.stroke()

      // Secondary traffic flow
      ctx.beginPath()
      ctx.strokeStyle = "#10b981"
      ctx.lineWidth = 3
      ctx.globalAlpha = 0.6
      for (let x = 20; x <= 380; x += 2) {
        const y = 200 + Math.cos((x + time * 80) * 0.015) * 15
        if (x === 20) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }
      ctx.stroke()
      ctx.globalAlpha = 1

      // Draw nodes with enhanced styling
      nodes.forEach((node) => {
        let nodeColor = "#06b6d4"
        let nodeSize = 8
        let glowColor = "#06b6d4"

        switch (node.status) {
          case "optimal":
            nodeColor = "#10b981"
            glowColor = "#10b981"
            break
          case "congested":
            nodeColor = "#ef4444"
            glowColor = "#ef4444"
            break
          case "warning":
            nodeColor = "#f59e0b"
            glowColor = "#f59e0b"
            break
          case "offline":
            nodeColor = "#6b7280"
            glowColor = "#6b7280"
            break
        }

        if (node.type === "hub") {
          nodeSize = 12
        } else if (node.type === "sensor") {
          nodeSize = 5
        }

        // Draw glow effect
        ctx.beginPath()
        ctx.arc(node.x, node.y, nodeSize + 4, 0, 2 * Math.PI)
        ctx.fillStyle = glowColor + "40"
        ctx.fill()

        // Draw main node
        ctx.beginPath()
        ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI)
        ctx.fillStyle = nodeColor
        ctx.fill()

        // Draw node border
        ctx.beginPath()
        ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI)
        ctx.strokeStyle = "#ffffff"
        ctx.lineWidth = 2
        ctx.stroke()

        // Add pulsing effect for active nodes
        if (node.status === "optimal" || node.status === "congested") {
          ctx.beginPath()
          ctx.arc(node.x, node.y, nodeSize + 6 + Math.sin(time * 2) * 2, 0, 2 * Math.PI)
          ctx.strokeStyle = nodeColor + "60"
          ctx.lineWidth = 2
          ctx.stroke()
        }

        // Draw traffic indicator for intersections
        if (node.type === "intersection" && node.traffic > 0) {
          ctx.fillStyle = "#ffffff"
          ctx.font = "10px Inter"
          ctx.textAlign = "center"
          ctx.fillText(node.traffic.toString(), node.x, node.y - nodeSize - 8)
        }
      })

      setAnimationFrame((prev) => prev + 1)
      requestAnimationFrame(animate)
    }

    animate()
  }, [nodes, animationFrame])

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // Find clicked node
    const clickedNode = nodes.find((node) => {
      const distance = Math.sqrt(Math.pow(x - node.x, 2) + Math.pow(y - node.y, 2))
      return distance <= (node.type === "hub" ? 12 : node.type === "sensor" ? 5 : 8)
    })

    setSelectedNode(clickedNode || null)
  }

  return (
    <div className="space-y-4">
      <div className="relative w-full h-80 bg-gradient-to-br from-slate-950 to-slate-900 rounded-xl overflow-hidden border border-slate-800/50">
        <canvas 
          ref={canvasRef} 
          width={400} 
          height={300} 
          className="w-full h-full cursor-pointer" 
          onClick={handleCanvasClick}
        />
        
        {/* Legend */}
        <div className="absolute top-4 left-4 space-y-2 bg-slate-900/80 backdrop-blur-sm rounded-lg p-3 border border-slate-700/50">
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
            <span className="text-orange-300">Primary Route</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
            <span className="text-emerald-300">Alternative Route</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-red-300">Congested</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-yellow-300">Warning</span>
          </div>
        </div>

        {/* Network Stats */}
        <div className="absolute top-4 right-4 bg-slate-900/80 backdrop-blur-sm rounded-lg p-3 border border-slate-700/50">
          <div className="text-xs text-slate-400 mb-1">Network Status</div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-emerald-400 font-medium">Active</span>
          </div>
        </div>
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-slate-200">{selectedNode.name}</h4>
              <Badge className={
                selectedNode.status === "optimal" ? "bg-emerald-500/20 text-emerald-400" :
                selectedNode.status === "congested" ? "bg-red-500/20 text-red-400" :
                selectedNode.status === "warning" ? "bg-yellow-500/20 text-yellow-400" :
                "bg-slate-500/20 text-slate-400"
              }>
                {selectedNode.status}
              </Badge>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-slate-400">Type</div>
                <div className="text-slate-200 capitalize">{selectedNode.type}</div>
              </div>
              <div>
                <div className="text-slate-400">Traffic</div>
                <div className="text-slate-200">{selectedNode.traffic} veh/hr</div>
              </div>
              <div>
                <div className="text-slate-400">Connections</div>
                <div className="text-slate-200">{selectedNode.connections.length}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
