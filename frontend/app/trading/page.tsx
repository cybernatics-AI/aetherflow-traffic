"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowLeft, TrendingUp, BarChart3, Coins, Activity, DollarSign, Zap } from "lucide-react"

interface MarketData {
  price: number
  change24h: number
  volume: number
  marketCap: number
}

interface OrderBookEntry {
  price: number
  quantity: number
  total: number
}

export default function TradingPage() {
  const [activeTab, setActiveTab] = useState("nfts")
  const [orderType, setOrderType] = useState("market")
  const [price, setPrice] = useState("")
  const [quantity, setQuantity] = useState("")
  const [marketData, setMarketData] = useState<MarketData>({
    price: 0.0847,
    change24h: 12.5,
    volume: 2847000,
    marketCap: 15600000,
  })

  const [buyOrders, setBuyOrders] = useState<OrderBookEntry[]>([
    { price: 0.0845, quantity: 1250, total: 105.625 },
    { price: 0.0844, quantity: 2100, total: 177.24 },
    { price: 0.0843, quantity: 890, total: 75.027 },
  ])

  const [sellOrders, setSellOrders] = useState<OrderBookEntry[]>([
    { price: 0.0849, quantity: 950, total: 80.655 },
    { price: 0.085, quantity: 1800, total: 153.0 },
    { price: 0.0851, quantity: 1200, total: 102.12 },
  ])

  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMarketData((prev) => ({
        ...prev,
        price: prev.price + (Math.random() - 0.5) * 0.001,
        change24h: prev.change24h + (Math.random() - 0.5) * 2,
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const handleTrade = () => {
    // Simulate trade execution
    console.log("Executing trade:", { orderType, price, quantity })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Mobile Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800/50 text-xs">
        <div className="flex items-center gap-2">
          <Activity className="w-3 h-3 text-green-400" />
          <span>Live</span>
        </div>
        <span className="font-mono">1:49 AM</span>
        <div className="flex items-center gap-1">
          <span>EN</span>
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        </div>
      </div>

      {/* Mobile Header */}
      <header className="flex items-center justify-between p-4 bg-slate-800">
        <Link href="/">
          <Button variant="ghost" size="sm" className="text-white hover:bg-slate-700">
            <ArrowLeft className="w-4 h-4" />
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-orange-400" />
          <span className="text-sm font-medium">Trading Desk</span>
        </div>
      </header>

      <div className="p-4 max-w-sm mx-auto space-y-4">
        {/* Market Overview */}
        <Card className="bg-slate-800/50 border-slate-600/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Coins className="w-4 h-4 text-orange-400" />
                <span className="font-semibold">AETHER/USD</span>
              </div>
              <Badge
                className={marketData.change24h >= 0 ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}
              >
                {marketData.change24h >= 0 ? "+" : ""}
                {marketData.change24h.toFixed(2)}%
              </Badge>
            </div>
            <div className="text-2xl font-bold mb-2">${marketData.price.toFixed(4)}</div>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-slate-400">24h Volume</span>
                <div className="font-semibold">${(marketData.volume / 1000000).toFixed(2)}M</div>
              </div>
              <div>
                <span className="text-slate-400">Market Cap</span>
                <div className="font-semibold">${(marketData.marketCap / 1000000).toFixed(1)}M</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tab Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-slate-800">
            <TabsTrigger value="nfts" className="data-[state=active]:bg-orange-600">
              NFTs
            </TabsTrigger>
            <TabsTrigger value="derivatives" className="data-[state=active]:bg-orange-600">
              Derivatives
            </TabsTrigger>
          </TabsList>

          <TabsContent value="nfts" className="space-y-4">
            {/* NFT Trading Interface */}
            <Card className="bg-slate-800/50 border-slate-600/50">
              <CardHeader>
                <CardTitle className="text-lg">NFT Marketplace</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Select defaultValue="traffic-data">
                  <SelectTrigger className="bg-slate-700 border-slate-600">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="traffic-data">Traffic Data NFT</SelectItem>
                    <SelectItem value="route-optimization">Route Optimization NFT</SelectItem>
                    <SelectItem value="eco-driver">Eco Driver Badge NFT</SelectItem>
                  </SelectContent>
                </Select>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm text-slate-400 mb-1 block">Floor Price</label>
                    <div className="flex items-center bg-slate-700 rounded-md px-3 py-2">
                      <DollarSign className="w-4 h-4 text-slate-400 mr-1" />
                      <span className="text-white">0.025</span>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-slate-400 mb-1 block">Available</label>
                    <div className="bg-slate-700 rounded-md px-3 py-2">
                      <span className="text-white">47</span>
                    </div>
                  </div>
                </div>

                <Button className="w-full bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700">
                  <Zap className="w-4 h-4 mr-2" />
                  Buy NFT
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="derivatives" className="space-y-4">
            {/* Derivatives Trading Interface */}
            <Card className="bg-slate-800/50 border-slate-600/50">
              <CardHeader>
                <CardTitle className="text-lg">Select Contract</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Select defaultValue="buy-sell">
                  <SelectTrigger className="bg-slate-700 border-slate-600">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="buy-sell">Buy/Sell</SelectItem>
                    <SelectItem value="long">Long Position</SelectItem>
                    <SelectItem value="short">Short Position</SelectItem>
                  </SelectContent>
                </Select>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm text-slate-400 mb-1 block">Price</label>
                    <div className="flex items-center">
                      <DollarSign className="w-4 h-4 text-slate-400 mr-2" />
                      <Input
                        type="number"
                        className="bg-slate-700 border-slate-600 text-right flex-1"
                        placeholder="0.00"
                        value={price}
                        onChange={(e) => setPrice(e.target.value)}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-slate-400 mb-1 block">Quantity</label>
                    <Input
                      type="number"
                      className="bg-slate-700 border-slate-600 text-right"
                      placeholder="0"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                    />
                  </div>
                </div>

                {/* Price Chart Placeholder */}
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-slate-400">Price Chart</span>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-3 h-3 text-green-400" />
                      <span className="text-xs text-green-400">+5.2%</span>
                    </div>
                  </div>
                  <svg className="w-full h-16" viewBox="0 0 200 50">
                    <path d="M10 40 Q50 20 80 30 T150 25 T190 20" stroke="#10b981" strokeWidth="2" fill="none" />
                    <circle cx="190" cy="20" r="2" fill="#10b981" />
                  </svg>
                </div>

                {/* Market Depth */}
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" />
                    Market Depth
                  </h4>

                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <div className="text-green-400 font-semibold mb-2">Bids</div>
                      {buyOrders.map((order, index) => (
                        <div key={index} className="flex justify-between py-1">
                          <span className="text-green-400">${order.price.toFixed(4)}</span>
                          <span className="text-slate-300">{order.quantity}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <div className="text-red-400 font-semibold mb-2">Asks</div>
                      {sellOrders.map((order, index) => (
                        <div key={index} className="flex justify-between py-1">
                          <span className="text-red-400">${order.price.toFixed(4)}</span>
                          <span className="text-slate-300">{order.quantity}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="text-center mt-3 pt-3 border-t border-slate-600">
                    <span className="text-xs text-slate-400">06/22/2025</span>
                  </div>
                </div>

                <Button
                  onClick={handleTrade}
                  className="w-full bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700"
                >
                  Execute Trade
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Portfolio Summary */}
        <Card className="bg-slate-800/50 border-slate-600/50">
          <CardContent className="p-4">
            <h4 className="font-semibold mb-3">Portfolio</h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-orange-400">128.45</div>
                <div className="text-xs text-slate-400">AETHER</div>
              </div>
              <div>
                <div className="text-lg font-bold text-green-400">$10.87</div>
                <div className="text-xs text-slate-400">USD Value</div>
              </div>
              <div>
                <div className="text-lg font-bold text-blue-400">+12.5%</div>
                <div className="text-xs text-slate-400">24h P&L</div>
              </div>
            </div>
          </CardContent>
        </Card>

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
          <Link href="/rewards" className="flex-1">
            <Button
              variant="outline"
              className="w-full border-orange-600 text-orange-400 bg-transparent hover:bg-orange-600 hover:text-white"
            >
              Rewards
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
