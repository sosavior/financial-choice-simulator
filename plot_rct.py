import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_rct_chart():
    # RCT Data from the terminal output
    labels = ['Control\n(Baseline)', 'Treatment A\n($500 Cash)', 'Treatment B\n(Sludge Eradication)', 'Treatment C\n(Synthesis)']
    rates = [41.4, 39.0, 41.5, 37.3]
    ate = [0.0, -2.4, 0.1, -4.1]

    # Set academic styling
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 12, 'font.family': 'sans-serif'})

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Custom color palette: Grey for control, muted red/blue for partials, bold purple for synthesis
    colors = ['#8C92AC', '#E27D60', '#85CDCB', '#412234']
    
    bars = ax.bar(labels, rates, color=colors, width=0.6)

    # Add data labels on top of the bars
    for bar, rate, effect in zip(bars, rates, ate):
        height = bar.get_height()
        # Capture Rate Label
        ax.text(bar.get_x() + bar.get_width()/2., height - 2.5,
                f'{rate}%', ha='center', va='bottom', color='white', fontweight='bold', fontsize=14)
        
        # ATE Label (skip for Control)
        if effect != 0.0:
            ate_text = f"ATE: {effect:+.1f}%"
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    ate_text, ha='center', va='bottom', color='#333333', fontweight='semibold', fontsize=11)

    # Format axes
    ax.set_ylabel('Debt Trap Capture Rate (%)', fontweight='bold')
    ax.set_title('Comparative RCT: Cash Transfers vs. Administrative Sludge Eradication', 
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_ylim(0, 50)
    
    # Clean up borders
    sns.despine(left=True)

    # Save the visualization
    os.makedirs("results", exist_ok=True)
    save_path = "results/rct_comparative_matrix.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Success. Publication-ready chart saved to {save_path}")

if __name__ == "__main__":
    generate_rct_chart()