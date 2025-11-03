"""
Visualization module for SkillLens MVP
Generates Plotly charts for coverage and skill distribution
"""
import plotly.graph_objects as go


def bar_coverage_chart(coverage: int, color: str = "#6366F1"):
    """
    Create a simple bar chart showing role coverage percentage.
    
    Args:
        coverage: Coverage percentage (0-100)
        color: Hex color for the bar (default: indigo)
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Bar(
        x=["Coverage"],
        y=[coverage],
        marker_color=color,
        text=[f"{coverage}%"],
        textposition='auto',
    ))
    fig.update_yaxes(range=[0, 100], title="Percentage")
    fig.update_layout(
        height=300,
        title="Role Coverage (%)",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def radar_skill_categories(extracted_by_cat: dict, color: str = "#6366F1"):
    """
    Create a radar/polar chart showing skill counts by category.
    
    Args:
        extracted_by_cat: Dict mapping category names to skill lists
        color: Hex color for the trace (default: indigo)
        
    Returns:
        Plotly Figure object
    """
    cats = list(extracted_by_cat.keys())
    vals = [len(extracted_by_cat[c]) for c in cats]
    
    # Format hover text with category name and count
    hover_text = [f"{cat.replace('_', ' ').title()}: {val} skills" for cat, val in zip(cats, vals)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=[c.replace('_', ' ').title() for c in cats],
        fill='toself',
        name='Skills',
        line_color=color,
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.3)",
        hovertext=hover_text,
        hoverinfo='text'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True
            )
        ),
        showlegend=False,
        height=400,
        title="Skills by Category",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
