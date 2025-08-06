"use client"

import { useEffect, useRef, useState } from "react"

interface DataPoint {
  timestamp: number
  vehicles: number
  efficiency: number
  co2Saved: number
}

export function RealtimeChart() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [dataPoints, setDataPoints] = useState<DataPoint[]>([])

  useEffect(() => {
    // Initialize with some data points
    const initialData: DataPoint[] = []
    const now = Date.now()
    for (let i = 0; i < 50; i++) {
      initialData.push({
        timestamp: now - (50 - i) * 1000,
        vehicles: 1400 + Math.random() * 200,
        efficiency: 80 + Math.random() * 20,
        co2Saved: 20 + Math.random() * 10,
      })
    }
    setDataPoints(initialData)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setDataPoints((prev) => {
        const newPoint: DataPoint = {
          timestamp: Date.now(),
          vehicles: 1400 + Math.random() * 200,
          efficiency: 80 + Math.random() * 20,
          co2Saved: 20 + Math.random() * 10,
        }
        return [...prev.slice(-49), newPoint]
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || dataPoints.length === 0) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const padding = 40

    ctx.clearRect(0, 0, width, height)

    // Draw grid
    ctx.strokeStyle = "#334155"
    ctx.lineWidth = 1
    for (let i = 0; i <= 5; i++) {
      const y = padding + (i * (height - 2 * padding)) / 5
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(width - padding, y)
      ctx.stroke()
    }

    // Draw vehicle count line
    ctx.strokeStyle = "#f97316"
    ctx.lineWidth = 2
    ctx.beginPath()
    dataPoints.forEach((point, index) => {
      const x = padding + (index * (width - 2 * padding)) / (dataPoints.length - 1)
      const y = height - padding - ((point.vehicles - 1200) / 400) * (height - 2 * padding)
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    ctx.stroke()

    // Draw efficiency line
    ctx.strokeStyle = "#10b981"
    ctx.lineWidth = 2
    ctx.beginPath()
    dataPoints.forEach((point, index) => {
      const x = padding + (index * (width - 2 * padding)) / (dataPoints.length - 1)
      const y = height - padding - ((point.efficiency - 60) / 40) * (height - 2 * padding)
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    ctx.stroke()

    // Draw labels
    ctx.fillStyle = "#94a3b8"
    ctx.font = "12px Inter"
    ctx.fillText("Vehicles", 10, 20)
    ctx.fillStyle = "#f97316"
    ctx.fillRect(70, 15, 10, 2)

    ctx.fillStyle = "#94a3b8"
    ctx.fillText("Efficiency", 10, 35)
    ctx.fillStyle = "#10b981"
    ctx.fillRect(70, 30, 10, 2)
  }, [dataPoints])

  return (
    <div className="w-full h-64 bg-slate-900/50 rounded-lg p-4">
      <canvas ref={canvasRef} width={600} height={200} className="w-full h-full" />
    </div>
  )
}
