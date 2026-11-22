# Draws the 1200x630 preview images shown when a BEEST chart page is shared (og:image).
# Run from the repo root; it writes PNGs into og/, which are then saved as JPG (social sites do not all accept WebP previews).
import json, datetime as dt
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import matplotlib.dates as mdates
for f in fm.findSystemFonts('/usr/share/fonts/opentype/inter'): fm.fontManager.addfont(f)
plt.rcParams['font.family']='Inter'
BG='#092142'; INK='#EEEEEE'; MUTED='#B8C0CC'; GRID=(238/255,238/255,238/255,0.12)
C={'gross':'#BB271A','net':'#CC43D6','gas':'#5CC971','hash':'#F19E4B','price':'#4397C7','bank':'#A9B4C2'}
rows=json.load(open('history.json'))['rows']
D=[dt.date.fromisoformat(r['date']) for r in rows]
last=D[-1]; lastlabel=last.strftime('%-d %b %Y')

def base(title, ylabel):
    fig=plt.figure(figsize=(12,6.3),dpi=100,facecolor=BG)
    fig.text(0.045,0.885,title,color=INK,fontsize=40,fontweight='bold',va='baseline')
    ax=fig.add_axes([0.105,0.15,0.75,0.62],facecolor=BG)
    for s in ax.spines.values(): s.set_visible(False)
    ax.grid(axis='y',color=GRID,lw=1); ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED,labelsize=19,length=0,pad=8)
    ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylabel(ylabel,color=MUTED,fontsize=18,labelpad=10)
    ax.set_xlim(D[0],last+dt.timedelta(days=10))
    fig.text(0.045,0.04,f'Source: BEEST 2 (batcoinz.com/beest), data to {lastlabel}',color='#8A96A6',fontsize=13,style='italic')
    return fig,ax

def endlabel(ax,x,y,text,color,dy=0,fs=24):
    ax.plot([x],[y],'o',color=color,ms=8,zorder=5)
    ax.annotate(text,(x,y),xytext=(12,dy),textcoords='offset points',color=color,fontsize=fs,fontweight='bold',va='center',annotation_clip=False)

def save(fig,name):
    ax=fig.axes[0]
    for _ in range(6):
        fig.canvas.draw(); r=fig.canvas.get_renderer()
        right=max(t.get_window_extent(r).x1 for t in ax.texts)/fig.bbox.width
        if right<=0.975: break
        b=ax.get_position(); ax.set_position([b.x0,b.y0,b.width-(right-0.97),b.height])
    fig.savefig('og/'+name.replace('og-','')+'.png',facecolor=BG); plt.close(fig)

# 1 Emissions
fig,ax=base('Bitcoin network emissions','Mt CO2e a year')
g=[r['gross_mt'] for r in rows]; n=[r['net_mt'] for r in rows]
ax.plot(D,g,color=C['gross'],lw=2.6); ax.plot(D,n,color=C['net'],lw=3.2)
ax.set_ylim(0,70)
endlabel(ax,last,g[-1],f"Total {g[-1]:.1f}",C['gross'],dy=14)
endlabel(ax,last,n[-1],f"Net {n[-1]:.1f}",C['net'],dy=-14)
save(fig,'og-emissions')

# 2 Mitigated
fig,ax=base('Bitcoin emissions mitigated','% of total emissions')
sh=[100*r['mitigation_gas_mt_30d']/r['gross_mt_30d'] if r.get('gross_mt_30d') else 0 for r in rows]
ax.plot(D,sh,color=C['gas'],lw=3.4); ax.set_ylim(0,15); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f'{v:.0f}%'))
endlabel(ax,last,sh[-1],f"{sh[-1]:.1f}%",C['gas'])
save(fig,'og-mitigated')

# 3 Intensity
fig,ax=base('Bitcoin carbon intensity','g CO2e per kWh')
ni=[r['intensity_g_kwh']*r['net_mt']/r['gross_mt'] for r in rows]
gi=[(d,r['grid_g_kwh']) for d,r in zip(D,rows) if r.get('grid_g_kwh')]
ax.plot([a for a,b in gi],[b for a,b in gi],color=C['bank'],lw=2.6)
ax.plot(D,ni,color=C['net'],lw=3.4); ax.set_ylim(0,650)
endlabel(ax,last,gi[-1][1],f"World grid {gi[-1][1]:.0f}",C['bank'],fs=22)
endlabel(ax,last,ni[-1],f"Bitcoin (net) {ni[-1]:.0f}",C['net'],fs=22)
save(fig,'og-intensity')

# 4 Growth (indexed, log)
fig,ax=base('Bitcoin growth vs emissions','Index, Sept 2019 = 1')
h0,p0,n0=rows[0]['hashrate_ehs_7d'],rows[0]['price_usd'],rows[0]['net_mt']
H=[r['hashrate_ehs_7d']/h0 for r in rows]; P=[r['price_usd']/p0 for r in rows]; N=[r['net_mt']/n0 for r in rows]
ax.set_yscale('log'); ax.set_ylim(0.4,20)
ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.5,1,2,5,10,20]))
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f'{v:g}x'))
ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.plot(D,P,color=C['price'],lw=1.6); ax.plot(D,N,color=C['net'],lw=1.9); ax.plot(D,H,color=C['hash'],lw=1.9)
endlabel(ax,last,H[-1],f"Hashrate {H[-1]:.1f}x",C['hash'],fs=22)
endlabel(ax,last,P[-1],f"Price {P[-1]:.1f}x",C['price'],fs=22)
endlabel(ax,last,N[-1],f"Net emissions {N[-1]:.1f}x",C['net'],fs=22)
save(fig,'og-growth')

# 5 Sustainable
fig,ax=base('Bitcoin sustainable energy use','% of mining power')
cs=[100*r['clean_share'] for r in rows]
ax.plot(D,cs,color=C['gas'],lw=3.4); ax.set_ylim(0,100)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f'{v:.0f}%'))
endlabel(ax,last,cs[-1],f"{cs[-1]:.1f}%",C['gas'])
save(fig,'og-sustainable')
print('ok')
