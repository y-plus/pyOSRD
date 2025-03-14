import plotly
import distinctipy

def train_colors(
    self,
) -> dict[str, str]:
    colors = (
        plotly.colors.qualitative.D3
        + 
        [
            '#%02x%02x%02x' % tuple(int(255*p) for p in c)
            for c in distinctipy.get_colors(
                len(self.trains),
                rng=42,
                pastel_factor=.2,
            )]
    )

    return dict(zip(self.trains, colors))