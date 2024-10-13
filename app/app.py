import os
import sys
import folium.plugins
from nicegui import ui
from pyosrd import OSRD
import folium


def render_map(
    m: folium.Map,
):
    m.get_root().width = "100%"
    m.get_root().height = "100%"
    return m.get_root()._repr_html_()


def space_time_charts_with_selector(sim):
    fig = sim.space_time_chart_plotly(sim.trains[0], points_to_show=['station'], eco_or_base='base')
    def update_graph():
        fig = sim.space_time_chart_plotly(train.value, points_to_show=['station'], eco_or_base='base')
        graph.update_figure(fig)
    with ui.column().classes('w-full h-[calc(100vh-80px)]'):
        train = ui.select(options=sim.trains, label='Train', value=sim.trains[0]).on_value_change(update_graph)
        graph = ui.plotly(fig).classes('w-full h-[calc(100vh-80px)]')


folder: str = sys.argv[1]
print(folder)
ref_sim = OSRD(dir=folder)

CASES = {
    'Reference': '',
    'Delayed with conflicts': 'delayed',
    'Interlocking only': 'propagate'
}
INV_CASES = {v: k for k, v in CASES.items()}

@ui.page('/')
def simulation(case: str | None = ''):

    if case=='delayed':
        sim = ref_sim.delayed()
        m = sim.folium_results(ref_sim=ref_sim, eco_or_base='base')    
    elif case=='reference' or case=='' or case is None:
        sim = ref_sim
        m = sim.folium_results(eco_or_base='base')
    else:
        sim = OSRD(
            dir=folder,
            infra_json='infra.json',
            simulation_json='simulation.json',
            results_json=os.path.join('delayed', case, 'results.json'),
            delays_json='delays.json',
        )
        m = sim.folium_results(ref_sim=ref_sim, eco_or_base='base')

    with ui.header(elevated=True).classes('bg-white text-black justify-between pl-5', replace='row items-center'):
        with ui.row().classes('items-center'):
            ui.image('app/logo_railwAI.png').on('click', lambda: ui.open('/')).classes('w-40 p-0 m-0 cursor-pointer')
 
            selector = ui.select(
                options=list(CASES.keys()),
                value=INV_CASES[case],
                on_change=lambda: ui.navigate.to(f"/?case={CASES[selector.value]}")
            )

        with ui.tabs(value='Map').classes('items-center text-primary').props('inline-label shrink') as tabs:
            info = ui.tab(name='Info',label='', icon='info').props('flat')
            map = ui.tab(name='Map',label='', icon='public').props('flat')
            get = ui.tab(name='SPACE-TIME',label='', icon="ssid_chart").props('flat')
            delays = ui.tab(name='Delays',label='', icon='area_chart').props('flat' if case else 'flat disabled')

    with ui.tab_panels(tabs, value=map).classes('w-full'):
        with ui.tab_panel(map).classes('p-0'):
            ui.html(render_map(m)).classes('w-full h-[calc(100vh-80px)] p-0')
        with ui.tab_panel(get).classes('p-0'):
            space_time_charts_with_selector(sim)
        if case:
            with ui.tab_panel(delays).classes('p-0'):
                ui.plotly(sim.delays_chart_plotly(ref_sim, eco_or_base='base')).classes('w-full')
        with ui.tab_panel(info).classes('p-0'):
            ui.label('info')

    with ui.right_drawer(value=False) as right_drawer:
        with ui.row().classes('justify-end w-full'):
            ui.button(icon='close', on_click=lambda: right_drawer.hide()).props('flat')
        with ui.row().classes('items-center justify-between w-full'):
            with ui.row():
                ui.icon('update').classes('text-2xl ')
                ui.label('Delays')
            ui.button('Add delay')
        with ui.row().classes('items-center'):
            ui.icon('error').classes('text-2xl')
            ui.label('Conflit')
        ui.button('Dispatch').classes('w-full')

ui.run(title='RailwAI | OSRD', favicon='🚉')
