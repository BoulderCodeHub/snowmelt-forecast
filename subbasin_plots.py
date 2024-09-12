import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime
def make_forecast_figure_CNRFC(forecast_snapshot):
  fig = go.Figure()
  colors_pct = ['rgba(205, 92, 92, 0.6)', 'rgba(227, 168, 87, 0.6)', 'rgba(146, 183, 254, 0.6)', 'rgba(70, 130, 180, 0.6)']
  max_val = 0
  min_val = 99999
  for bottom, top, color_use in zip(['10%', '25%', '50%', '75%'], ['25%', '50%', '75%', '90%'], colors_pct):
    fig.add_trace(go.Scatter(x = forecast_snapshot.index, y = forecast_snapshot[bottom], mode = 'lines', 
                    line =  dict(color =  'black', width = 0), showlegend = False, name = '', hovertemplate = '<b>%{text}</b>', 
                    text = ['',  '']))
    fig.add_trace(go.Scatter(x = forecast_snapshot.index, y = forecast_snapshot[top], mode = 'lines', 
                    line = dict(color = 'black', width = 0), fill = 'tonexty', 
                    fillcolor = color_use, showlegend = False, name = '', hovertemplate = '<b>%{text}</b>', 
                    text = ['',  '']))
    fig.add_trace(go.Scatter(x = forecast_snapshot.index, y = forecast_snapshot[bottom], mode = 'lines', 
                    line =  dict(color =  'black', width = 1.5), showlegend = False, name = '', hovertemplate = '<b>%{text}</b>', 
                    text = ['',  '']))
    max_val = max(max_val, np.max(forecast_snapshot[top]))
    min_val = min(max_val, np.min(forecast_snapshot[bottom]))

  plot_range = [forecast_snapshot.index[0], forecast_snapshot.index[-1]]
  fig.update_xaxes(title_text = 'Forecasted Date', showline = False, linecolor = 'black', ticks = 'outside',
             tickmode = 'array', tickvals = plot_range, ticktext= [str(plot_range[0].month) + '/' + str(plot_range[0].year), str(plot_range[0].month) + '/' + str(plot_range[-1].year)],
             tickfont = dict(family = 'Droid Sans', size = 12, color = 'black'),
             tickwidth = 0.0, tickcolor = 'black', showgrid=False,
             range =  plot_range,
             rangeslider=dict(visible=True),
             visible = True)
             
  fig.update_yaxes(title_text =  'Forecasted Flow', showline = False, linecolor = 'black', ticks = 'outside',
             tickfont = dict(family = 'Droid Sans', size = 12, color = 'black'),
             tickwidth = 0.0, tickcolor = 'black', showgrid=False,
             range = [max(min_val * 0.95, 0), max_val * 1.1],
             visible = True)

  fig.update_layout(legend=dict(yanchor="top", y=0.975, xanchor="left", x=0.025, title_font_family="Droid Sans",
             font=dict(size= 10), tracegroupgap = 0, bgcolor = 'rgba(250, 250, 250, 0.0)'), margin=dict(l=0,r=0,b=0,t=0), width=650, height=400)

  return fig  
  
def make_forecast_figure_CBRFC(forecast_snapshot):
  fig = go.Figure()
  colors_pct = ['rgba(205, 92, 92, 0.6)', 'rgba(227, 168, 87, 0.6)', 'rgba(146, 183, 254, 0.6)', 'rgba(70, 130, 180, 0.6)']
  max_val = 0
  min_val = 99999
  num_timesteps = len(forecast_snapshot.index)
  num_esp = len(forecast_snapshot.columns)
  sorted_rows = np.sort(forecast_snapshot.values[:,1:], axis = 1)
  print(sorted_rows)
  percentile_vals = np.zeros((num_timesteps, 5))
  percentile_df = pd.DataFrame(index = forecast_snapshot.index)
  for frac_cnt, fraction in enumerate([0.1, 0.25, 0.5, 0.75, 0.9]):
    for index_cnt in range(0, len(forecast_snapshot.index)):
      percentile_vals[index_cnt, frac_cnt] = sorted_rows[index_cnt, int(fraction * float(num_esp))] * 1.0
  percentile_labels = ['10%', '25%', '50%', '75%', '90%']
  for bottom, top, color_use in zip([0, 1, 2, 3], [1, 2, 3, 4], colors_pct):
    fig.add_trace(go.Scatter(x = forecast_snapshot.index, y = percentile_vals[:,bottom], mode = 'lines', 
                    line =  dict(color =  'black', width = 0), showlegend = False, name = '', hovertemplate = '<b>%{text}</b>', 
                    text = ['On ' + str(forecast_snapshot.index[i].month) + '/' + str(forecast_snapshot.index[i].year) + ': ' + percentile_labels[bottom] +  ' chance supply is less than {}'.format(percentile_vals[i, bottom]) for i in range(len(forecast_snapshot.index))]))
    fig.add_trace(go.Scatter(x = forecast_snapshot.index, y = percentile_vals[:,top], mode = 'lines', 
                    line = dict(color = 'black', width = 0), fill = 'tonexty', 
                    fillcolor = color_use, showlegend = False, name = '', hovertemplate = '<b>%{text}</b>', 
                    text = ['On ' + str(forecast_snapshot.index[i].month) + '/' + str(forecast_snapshot.index[i].year) + ': ' + percentile_labels[bottom] + '-' + percentile_labels[top] +  ' chance supply is between {}'.format(percentile_vals[i, bottom]) + ' and {}'.format(percentile_vals[i, top]) for i in range(len(forecast_snapshot.index))]))
    fig.add_trace(go.Scatter(x = forecast_snapshot.index, y = percentile_vals[:,bottom], mode = 'lines', 
                    line =  dict(color =  'black', width = 0.5), showlegend = False, name = '', hovertemplate = '<b>%{text}</b>', 
                    text = ['On ' + str(forecast_snapshot.index[i].month) + '/' + str(forecast_snapshot.index[i].year) + ': ' + percentile_labels[bottom] +  ' chance supply is less than {}'.format(percentile_vals[i, bottom]) for i in range(len(forecast_snapshot.index))]))
    max_val = max(max_val, np.max(percentile_vals[:,top]))
    min_val = min(max_val, np.min(percentile_vals[:,bottom]))
  fig.add_trace(go.Scatter(x = forecast_snapshot.index, y = percentile_vals[:,top], mode = 'lines', 
                  line =  dict(color =  'black', width = 0.5), showlegend = False, name = '', hovertemplate = '<b>%{text}</b>', 
                  text = ['On ' + str(forecast_snapshot.index[i].month) + '/' + str(forecast_snapshot.index[i].year) + ': ' + percentile_labels[top] +  ' chance supply is less than {}'.format(percentile_vals[i, top]) for i in range(len(forecast_snapshot.index))]))

  plot_range = [forecast_snapshot.index[0], forecast_snapshot.index[-1]]
  tick_range = []
  tick_labs = []
  for year_cnt in range(forecast_snapshot.index[0].year, forecast_snapshot.index[-1].year + 1):
    tick_range.append(datetime(year_cnt, forecast_snapshot.index[0].month, 1, 0, 0))
    tick_labs.append(str(forecast_snapshot.index[0].month) + '/' + str(year_cnt))
  fig.update_xaxes(title_text = 'Forecasted Date', showline = False, linecolor = 'black', ticks = 'outside',
             tickmode = 'array', tickvals = tick_range, ticktext= tick_labs,
             tickfont = dict(family = 'Droid Sans', size = 12, color = 'black'),
             tickwidth = 0.0, tickcolor = 'black', showgrid=False,
             range =  plot_range,
             visible = True,
             rangeslider=dict(visible=True),
             ) 
  fig.update_yaxes(title_text =  'Forecasted Flow', linecolor = 'black', ticks = 'outside',
             tickfont = dict(family = 'Droid Sans', size = 12, color = 'black'),
             tickwidth = 0.0, tickcolor = 'black', showgrid=False,
             range = [max(min_val * 0.95, 0), max_val * 1.1],
             visible = True)
  fig.update_layout(legend=dict(yanchor="top", y=0.975, xanchor="left", x=0.025, title_font_family="Droid Sans",
             font=dict(size= 10), tracegroupgap = 0, bgcolor = 'rgba(250, 250, 250, 0.0)'), margin=dict(l=0,r=0,b=0,t=0), width=650, height=400)
  return fig  