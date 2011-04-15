#!/bin/sh

R --no-save <<EOF
data = read.table("commitcount.txt")
pdf("plot.pdf", width=16, height=9)
par(omd = c(.15, .85, .15, .85))
mp <- barplot(data[,2])
axis(2)
axis(1, at = mp, labels = data[,1], cex.axis = 2, las=2)
dev.off()
EOF
