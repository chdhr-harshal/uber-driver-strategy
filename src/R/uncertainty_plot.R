#! /usr/local/bin/RScript

library(data.table)
library(ggplot2)
library(ggthemes)

# Set working directories
setwd("~/bu/Desktop/uber_driver_strategy/")
figures.dir = "~/bu/Desktop/uber_driver_strategy/plots/"

# Read data
dd = data.table(read.delim("./plots_data/uncertainty_evolution_1.csv",
                           sep=","))
dd[, strategy := factor(strategy, levels=c("naive", "reloc", "flexi", "reloc_flexi"))]
levels(dd$strategy) = c("naive", "relocation", "flexible", "flexible-relocation")

# Uncertainty earnings evolution plot
mycols = c("orange", "red", "darkgreen", "blue")
p = ggplot(data=dd, aes(x=uncertainty, y=earnings))
p = p + geom_line(aes(color=strategy, group=strategy))
p = p + geom_point(aes(color=strategy), size=0.5)
p = p + scale_x_continuous(breaks=seq(0,0.99,0.1))
p = p + xlab(expression(paste("Uncertainty level (", alpha, ")")))
p = p + scale_y_continuous(name="Earnings ($ / workday)", breaks=seq(0,500,100) )
p = p + scale_color_manual(name="", values=mycols)
p = p + theme_bw()
p = p + theme(legend.position = c(0.5,0.4),
              legend.direction = "horizontal",
              legend.title = element_blank(),
              legend.text = element_text(size = 5, face="italic"),
              axis.text.x = element_text(size = 5),
              axis.text.y = element_text(size = 5),
              axis.title.y = element_text(size = 7),
              axis.title.x = element_text(size = 7),
              legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
              legend.key.size = unit(0.2, "cm"))
p
ggsave(paste0(figures.dir, "uncertainty_evolution.pdf"), w=8.5, h=4, units="cm")
