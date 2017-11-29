#! /usr/local/bin/RScript
library(readr)
library(data.table)
library(ggplot2)
library(ggthemes)
library(ggmap)
library(geojsonio)
library(rgdal)
library(sp)
library(maps)
library(maptools)
library(grid)

# Set working directories
setwd("~/bu/Desktop/uber_driver_strategy/")
figures.dir = "~/bu/Desktop/uber_driver_strategy/plots/"

# Read the geojson file
city_zones = geojson_read("./data/taxi_zones/taxi_zones.geojson", what="sp")
city_zones = fortify(city_zones, region='taxi_zone')
city_zones_df = data.table(city_zones)

# Read demands data
surge_df = data.table(read.delim("./plots_data/surge_heatmap.csv.gz", sep=","))

# Merge dataframes
dd = merge(city_zones_df, surge_df, by.x='id', by.y='zone', all.x=TRUE, allow.cartesian=TRUE)
dd[, unsuccessful := as.numeric(unsuccessful)]
dd[, time := as.factor(time)]
# dd[, surge_multiplier := as.factor(surge_multiplier)]
levels(dd$time) = c("Morning 8AM", "Noon 12PM", "Evening 5PM", "Night 10PM")

# Plot on map
mycol = c("yellow","red", "navy")
p0 = ggmap(get_map(c(lon=-74.0, lat=40.74), scale="auto", zoom=10, maptype="roadmap", color="bw"), 
           extent="device")
p = p0 + facet_wrap(~time)
p = p + geom_polygon(aes(long, lat, group = group, fill=surge_multiplier),
                     data=dd[time == "Morning 8AM" | time == "Evening 5PM"],
                     alpha=0.8,
                     size=0.2,
                     colour="black")
p = p + scale_fill_gradientn(name="Surge\nmultiplier", colors = mycol)
p = p + scale_x_continuous(name="", expand = c(0,0), limits=c(-74.3, -73.7))
p = p + scale_y_continuous(name="", expand = c(0,0), limits=c(40.48, 40.91))
p = p + theme_few()
p = p + theme(strip.background = element_blank(),
              axis.line = element_blank(),
              axis.title = element_blank(),
              axis.ticks = element_blank(),
              axis.text = element_blank(),
              strip.text.x = element_text(size = 6),
              legend.position = c(0.08,0.75),
              legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
              legend.key.size = unit(0.2, "cm"),
              legend.title = element_text(size = 5),
              legend.text = element_text(size = 5),
              plot.margin = unit(c(0,0.2,0,0), 'cm'))
p
ggsave(paste0(figures.dir, "surge_heatmap.pdf"), w=8, h=8, units="cm")
