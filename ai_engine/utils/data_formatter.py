def format_for_heatmap(results):
    """
    Format bias results for a frontend heatmap component.
    Extracts latitude, longitude, and maps bias to a weight.
    """
    heatmap_data = []
    for item in results:
        # Use abs(bias_score) for heat intensity
        weight = abs(item.get("bias_score", 0))
        
        heatmap_data.append({
            "lat": item.get("lat", 0),
            "lng": item.get("lng", 0),
            "weight": weight,
            "area": item.get("area", "Unknown"),
            "bias_percentage": item.get("bias_percentage", 0)
        })
        
    return heatmap_data