import streamlit as st
import pandas as pd
import numpy as np
from stqdm import stqdm
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from PIL import Image
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

st.set_page_config(page_title='Pokémon TCGP Ranked Sims', page_icon='https://assets.pokemon.com/static2/_ui/img/favicon.ico')
st.title('Pokémon TCGP Ranked Sims')
st.text(
    '''
    Enter a Win Rate and initial number of points and this app will simulate thousands of seasons at that win rate and starting points value to determine how many games need to be played to reach Master Ball rank. 
    
    Seasons take into consideration win streak bonuses and rank-specific loss penalties. 
    
    Win rates under 0.400 take too long to simulate, and aren't guaranteed to reach Master Ball rank. Win rates above 0.800 aren't included, because they make me jealous.
    '''
)

### Styling
text_color = '#ffcb00'
background_color = '#1a3871'

sns.set_theme(
    style={
        'axes.edgecolor': text_color,
        'axes.facecolor': background_color,
        'axes.labelcolor': text_color,
        'xtick.color': text_color,
        'ytick.color': text_color,
        'figure.facecolor':background_color,
        'grid.color': background_color,
        'grid.linestyle': '-',
        'legend.facecolor':background_color,
        'text.color': text_color
     }
    )

ball_colors = {
    'Poké Ball':['#ed533A','#ffffff'],
    'Great Ball':['#0075ab','#ed533a'],
    'Ultra Ball':['#f6d044','#515151'],
    'Master Ball':['#5f4691','#e566ac']
    }

# Font
github_url = 'https://github.com/Blandalytics/poke_tcgp/blob/main/PokemonGb-RAeo.ttf?raw=true'
response = urlopen(github_url)
f = NamedTemporaryFile(delete=False, suffix='.ttf')
f.write(response.read())
f.close()
prop = fm.FontProperties(fname=f.name)

### Data
# Core gameplay values
ball_ranks = {
    'Beginner 1':0,
    'Beginner 2':20,
    'Beginner 3':50,
    'Beginner 4':95,
    'Poké Ball 1':145,
    'Poké Ball 2':195,
    'Poké Ball 3':245,
    'Poké Ball 4':300,
    'Great Ball 1':355,
    'Great Ball 2':420,
    'Great Ball 3':490,
    'Great Ball 4':600,
    'Ultra Ball 1':710,
    'Ultra Ball 2':860,
    'Ultra Ball 3':1010,
    'Ultra Ball 4':1225,
    'Master Ball 1':1450}

streak_points = {
    1:0,
    2:3,
    3:6,
    4:9,
    5:12
}

loss_points = {
    'Beginner':0,
    'Poké Ball':-5,
    'Great Ball':-5,
    'Ultra Ball':-7,
    'Master Ball':-10
}
WIN_POINTS = 10

# Simmed Games to Master Ball for given win rates
win_rate_dict = {
    0.4: 1484.926, 0.41: 1194.887, 0.42: 982.132, 0.43: 843.68, 0.44: 738.012,
    0.45: 650.127, 0.46: 589.231, 0.47: 538.258, 0.48: 493.09, 0.49: 459.009,
    0.5: 424.525, 0.51: 393.153, 0.52: 367.034, 0.53: 346.537, 0.54: 326.463,
    0.55: 310.332, 0.56: 293.679, 0.57: 276.407, 0.58: 264.246, 0.59: 253.089,
    0.6: 240.926, 0.61: 231.919, 0.62: 219.51, 0.63: 211.928, 0.64: 203.88,
    0.65: 195.79, 0.66: 188.951, 0.67: 181.143, 0.68: 174.944, 0.69: 167.794,
    0.7: 162.673, 0.71: 157.054, 0.72: 152.025, 0.73: 147.737, 0.74: 141.183,
    0.75: 136.461, 0.76: 133.371, 0.77: 129.334, 0.78: 125.196, 0.79: 121.398,
    0.8: 117.115
    }

col1, col2, col3, col4, col5 = st.columns(5)
# Input Variables
with col2:
    win_rate = st.number_input("Win rate:", 
                               min_value=0.4, max_value=0.8, value=0.6,
                               step=0.001, format="%0.3f")
with col4:
    initial_points = st.number_input("Starting Points:", min_value=0, max_value=1225)
    sim_seasons = int(round(1000*10**(10*(min(win_rate,0.5)-0.4))))
    needed_battles = int(win_rate_dict[int(round(win_rate*100,0))/100]*sim_seasons)
    
    initial_rank = [(ball_rank, points) for ball_rank, points in ball_ranks.items() if initial_points >= points][-1][0]
    
    total_games_needed = []
    rank_games_needed = []
    
    progress_text = f"Challenging {needed_battles/1000000:,.1f}M trainers to battle"

my_bar = st.progress(0, text=progress_text)

for season in range(sim_seasons):
    my_bar.progress((season + 1)/sim_seasons, text=progress_text)
    win_streak = 0
    season_points = initial_points
    current_rank = initial_rank
    games_played = 0
    games_needed = {'Beginner':0}
    wins = 0
    while season_points < ball_ranks['Master Ball 1']:
        games_played += 1
        if np.random.random() <= win_rate:
            wins += 1
            sim_win_rate = wins/games_played
            win_streak += 1
            season_points += WIN_POINTS + streak_points[min(5,win_streak)]
            new_rank = [(tool, value) for tool, value in ball_ranks.items() if season_points >= value][-1][0]
            if current_rank != new_rank:
                current_rank = new_rank
            if new_rank[:-2] not in games_needed.keys():
              games_needed.update({new_rank[:-2]:games_played})
        else:
            sim_win_rate = wins/games_played
            win_streak = 0
            season_points += loss_points[current_rank[:-2]]
            new_rank = [(tool, value) for tool, value in ball_ranks.items() if season_points >= value][-1][0]
            if current_rank != new_rank:
                current_rank = new_rank
    rank_games_needed += [games_needed]
    total_games_needed += [games_played]
if initial_rank[:-2] in games_needed.keys():
    games_needed.pop(initial_rank[:-2],None)
avg_games_needed = sum(total_games_needed)/len(total_games_needed)
rank_df = pd.DataFrame(rank_games_needed)

useful_ranks = ['Poké Ball','Great Ball','Ultra Ball','Master Ball']
useful_ranks = [x for x in useful_ranks if x in games_needed.keys()]
my_bar.empty()

# Initiate figure
def plot_sims(avg_games_needed, rank_df, useful_ranks):
    fig, ax = plt.subplots(figsize=(10,4))
    
    # Loop through ranks
    for season_rank in useful_ranks:
        sns.kdeplot(rank_df[season_rank],
                    cut=0,
                    common_grid=True,
                    color=ball_colors[season_rank][0],
                    fill=True,
                    alpha=1,
                    linewidth=1,
                    edgecolor=ball_colors[season_rank][1])
        
    # If not starting from 0, update title text
    if initial_points != 0:
        points_text = f' and {initial_points:,.0f} points'
        addl_text = ' more'
    else:
        points_text = ''
        addl_text = ''
    
    ## Chart formatting
    # Add gutter to the horizontal ends of the chart
    x_axis_buffer = rank_df[useful_ranks].max().max()/10
    ax.set(xlim=(-x_axis_buffer,
                 rank_df[useful_ranks].max().max()+x_axis_buffer),
           ylim=(ax.get_ylim()[1]*0.0025,ax.get_ylim()[1]*1.5)
           )
    # Set X label w custom font
    ax.set_xlabel('Games Played',fontproperties=prop)
    
    # Add lines and text boxes to each rank
    # Need to do this here, since it relies on the defined ylim above
    # (And I'm too lazy to set it up to calculate that ahead of time)
    for season_rank in useful_ranks:
        vert_frac = (len(useful_ranks)-useful_ranks.index(season_rank))/len(useful_ranks)
        avg_games = rank_df[season_rank].mean()
        ax.axvline(avg_games,
                   color=ball_colors[season_rank][1],
                   ymax=vert_frac*0.85,
                   linewidth=2)
        ax.text(avg_games,
                ax.get_ylim()[1]*vert_frac*0.85,
                f'{season_rank}\n{avg_games:,.0f} games',
                ha='left',
                va='center',
                fontsize=12,
                color=ball_colors[season_rank][1],
                fontproperties=prop,
                bbox={'facecolor':ball_colors[season_rank][0],
                      'edgecolor':ball_colors[season_rank][1],
                      'linewidth':3,
                      'boxstyle':'round'}
                )
    
    # Custom font for X-axis
    ax.set_xticklabels([int(x) for x in ax.get_xticks()], fontproperties=prop)
    # Hide Y-axis
    ax.yaxis.set_visible(False)
    
    # Custom title w custom font
    fig.suptitle(f'Given a {win_rate:.3f} Win Rate{points_text}, it will\ntake {avg_games_needed:,.0f}{addl_text} games to hit Master Ball rank',y=1,
                 fontproperties=prop,
                 fontsize=12
                 )
    sns.despine(left=True,bottom=True)
    st.pyplot(fig)
plot_sims(avg_games_needed, rank_df, useful_ranks)

def load_logo():
    logo_loc = 'https://github.com/Blandalytics/poke_tcgp/blob/main/blandalytics_poke.png?raw=true'
    img_url = urlopen(logo_loc)
    logo = Image.open(img_url)
    return logo
    
logo = load_logo()
st.image(logo, width=200)
st.write('Find me at [blandalytics.pitcherlist.com](https://bsky.app/profile/blandalytics.pitcherlist.com)\n')
st.header('Assumptions')
st.write(
    '''
    The basis for these assumptions can be found [here](https://www.pokemon-zone.com/articles/ranked-match-guide-tcg-pocket/). 
    
    Win Streak Bonuses: 
    - 2 Wins: 3 pts 
    - 3 Wins: 6 pts 
    - 4 Wins: 9 pts 
    - 5+ Wins: 12 pts 
    
    Loss Penalties: 
    - Beginner: 0 pts 
    - Poké Ball: 0 pts 
    - Great Ball: -5 pts 
    - Ultra Ball: -7 pts 
    - Master Ball: -10 pts
    
    Point threshold per rank: 
    - Beginner 1: 0 pts 
    - Beginner 2: 20 pts 
    - Beginner 3: 50 pts 
    - Beginner 4: 95 pts 
    - Poké Ball 1: 145 pts 
    - Poké Ball 2: 195 pts 
    - Poké Ball 3: 245 pts 
    - Poké Ball 4: 300 pts 
    - Great Ball 1: 355 pts
    - Great Ball 2: 420 pts
    - Great Ball 3: 490 pts
    - Great Ball 4: 600 pts 
    - Ultra Ball 1: 710 pts 
    - Ultra Ball 2: 860 pts 
    - Ultra Ball 3: 1010 pts 
    - Ultra Ball 4: 1225 pts 
    - Master Ball: 1450 pts
    '''
)
