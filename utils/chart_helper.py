"""
Chart Helper
Utilities for creating charts with matplotlib
"""
from typing import List, Dict, Any
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates


class ChartHelper:
    """Helper class for creating charts"""
    
    @staticmethod
    def create_timeline_chart(timeline_data: List[Dict[str, Any]], 
                            test_name: str,
                            normal_min: float = None,
                            normal_max: float = None,
                            figsize: tuple = (10, 6)) -> Figure:
        """
        Create a line chart for test result timeline
        
        Args:
            timeline_data: List of dicts with 'date' and 'value' keys
            test_name: Name of the test for chart title
            normal_min: Normal range minimum (optional)
            normal_max: Normal range maximum (optional)
            figsize: Figure size tuple (width, height)
        
        Returns:
            matplotlib Figure object
        """
        # Extract dates and values
        dates = [item['date'] for item in timeline_data if item.get('value') is not None]
        values = [item['value'] for item in timeline_data if item.get('value') is not None]
        
        if not dates or not values:
            # Return empty figure if no data
            fig = Figure(figsize=figsize)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Không có dữ liệu', 
                   ha='center', va='center', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create figure
        fig = Figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        # Plot main line
        ax.plot(dates, values, marker='o', linestyle='-', linewidth=2, 
               markersize=8, color='#2196F3', label='Kết quả')
        
        # Plot normal range if provided
        if normal_min is not None:
            ax.axhline(y=normal_min, color='green', linestyle='--', 
                      linewidth=1, alpha=0.7, label=f'Giới hạn dưới: {normal_min}')
        
        if normal_max is not None:
            ax.axhline(y=normal_max, color='green', linestyle='--', 
                      linewidth=1, alpha=0.7, label=f'Giới hạn trên: {normal_max}')
        
        # Fill normal range area
        if normal_min is not None and normal_max is not None:
            ax.fill_between(dates, normal_min, normal_max, 
                           color='green', alpha=0.1)
        
        # Formatting
        ax.set_xlabel('Ngày xét nghiệm', fontsize=11)
        ax.set_ylabel('Giá trị', fontsize=11)
        ax.set_title(f'Biểu đồ theo dõi: {test_name}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        fig.autofmt_xdate()  # Rotate date labels
        
        # Tight layout
        fig.tight_layout()
        
        return fig
    
    @staticmethod
    def create_bar_chart(categories: List[str], values: List[float],
                        title: str, xlabel: str = "", ylabel: str = "",
                        figsize: tuple = (10, 6)) -> Figure:
        """
        Create a bar chart
        
        Args:
            categories: List of category names
            values: List of values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size tuple
        
        Returns:
            matplotlib Figure object
        """
        fig = Figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        # Create bars
        bars = ax.bar(categories, values, color='#2196F3', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=10)
        
        # Formatting
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Rotate x labels if needed
        if len(categories) > 5:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        
        return fig
    
    @staticmethod
    def save_figure(fig: Figure, filepath: str, dpi: int = 100):
        """Save figure to file"""
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
