library(httr)
library(sf)
library(sp)
library(tmap)
library(tmaptools)
library(classInt)
library(rgdal)
library(raster)
library(rgeos)
library(ggplot2)
library(spData)
library(gstat)
library(spatstat)
library(maptools)
library(corrplot)
library(spdep)
library(spatstat)

envelope(cafe_pnts, fun= Kest, nsim= n, verbose=F)

n <- 10
sporeK <- envelope(cafe_pnts.ppp, fun= Kest, nsim= n, verbose=F)
plot(sporeK)

WGS84 <- "+init=epsg:4326"
CANLAM <-"+init=epsg:3347"
# mtl_trajet <- read_shape("../../app_route_data/land_use_mtl_trajet.shp", as.sf = FALSE)
# cafe_pnts <- read.csv("../../data/cafe_pnts.csv")
mtl_dissem <- readOGR("../../shapes/mtl_dissem.geojson")
cafe_pnts_sf = read_sf("../../shapes/cafe_pnts.shp")

mtl_dissem_union <- rgeos::gUnaryUnion(mtl_dissem)

# Point pattern
cafe_pnts <- st_transform(cafe_pnts, crs=CANLAM)
mtl_dissem <- spTransform(mtl_dissem, CANLAM)

window <- as.owin(mtl_dissem_union)
plot(window, main= "Window used for K function")
is.numeric(cafe_pnts$x)
cafe_pnts <- read_shape("../../shapes/cafe_pnts.shp", current.projection = CANLAM, as.sf = FALSE)
cafe_pnts.ppp <- ppp(x=cafe_pnts$x,y=cafe_pnts$y,window=window)
K <- Kest(cafe_pnts.ppp, correction="border")
plot(K, main = "Leisure", xlab = "Distance (m)",key.width = lcm(1.8))
plot(density(cafe_pnts.ppp, sigma = 1000))
