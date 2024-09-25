from nicegui import ui
from pyosrd import OSRD
import folium
from folium import plugins



def render_map(
    m: folium.Map,
):
    m.get_root().width = "100%"
    m.get_root().height = "100%"
    return m.get_root()._repr_html_()


def space_time_charts_with_selector(sim):
    fig = sim.space_time_chart_plotly(sim.trains[0], points_to_show=['station'], eco_or_base='eco')
    def update_graph():
        fig = sim.space_time_chart_plotly(train.value, points_to_show=['station'], eco_or_base='eco')
        graph.update_figure(fig)
    train = ui.select(options=sim.trains, label='Train', value=sim.trains[0]).on_value_change(update_graph)
    graph = ui.plotly(fig).classes('w-full h-[calc(100vh-80px)]')


folder: str = 'notebooks/c1_3trains'
ref_sim = OSRD(dir=folder)


@ui.page('/')
def simulation(delayed: str = ''):

    if delayed:
        sim = ref_sim.delayed()
        m = sim.folium_results(ref_sim=ref_sim, eco_or_base='eco')    
    else:
        sim = ref_sim
        m = sim.folium_results(eco_or_base='eco')

    with ui.header(elevated=True).classes('bg-white text-black items-center justify-between py-2'):
        with ui.row().classes('items-center'):
            ui.image('app/logo_railwAI.png').on('click', lambda: ui.open('/')).classes('w-40 p-0 m-0 cursor-pointer')
            ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat')
        with ui.row().classes('items-center'):
            ui.button(icon='public', on_click=lambda: (map.set_visibility(True), get.set_visibility(False), el.set_visibility(False))).props('flat')
            ui.button(icon="ssid_chart", on_click=lambda: (map.set_visibility(False), get.set_visibility(True), el.set_visibility(False))).props('flat')
            if delayed:
                ui.button(icon='area_chart', on_click=lambda: (map.set_visibility(False), get.set_visibility(False),el.set_visibility(True))).props('flat')
        with ui.row().classes('items-center'):        
            ui.button('Add delay', icon='update', on_click=lambda: right_drawer.show()).props('outline rounded disabled')
            ui.button('Dispatch', icon='published_with_changes', on_click=lambda: right_drawer.show()).props('outline rounded disabled')

    with ui.left_drawer(value=False) as left_drawer:
        with ui.row().classes('justify-end w-full'):
            ui.button(icon='close', on_click=lambda: left_drawer.hide()).props('flat')
        with ui.button('Case', icon='folder_open').props('flat'):
            ui.tooltip('Open case ...').props('anchor="center right" self="center left" ')
        with ui.button('Info', icon='info').props('flat'):
            ui.tooltip('Trains, stations, delays ...').props('anchor="center right" self="center left" ')
        with ui.button('Reference', icon='checklist_rtl', on_click=lambda: ui.navigate.to("/")).props('flat'):
            ui.tooltip('Reference schedule').props('anchor="center right" self="center left" ')
        with ui.button('Delayed', icon='railway_alert', on_click=lambda: ui.navigate.to("/?delayed=true")).props('flat'):
            ui.tooltip('Delayed schedule (interlocking only)').props('anchor="center right" self="center left" ')
        with ui.button('Dispatched', icon='published_with_changes').props('flat'):
            ui.tooltip('Dispatched schedules').props('anchor="center right" self="center left" ') 

    map = ui.html(render_map(m)).classes('w-full h-[calc(100vh-80px)]')
    with ui.element().classes('w-full h-[calc(100vh-80px)]') as get:
        space_time_charts_with_selector(sim)
    if delayed:
        with ui.element().classes('w-full h-[calc(100vh-80px)]') as el:
            ui.plotly(sim.delays_chart_plotly(ref_sim, eco_or_base='eco')).classes('w-full h-[calc(100vh-80px)]')

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
