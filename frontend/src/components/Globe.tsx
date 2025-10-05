'use client';

import React, { forwardRef, useImperativeHandle, useEffect, useRef } from 'react';

interface GlobeRef {
  zoomToCountry: (country: any) => void;
  selectCountry: (country: any, isSearchSelection?: boolean) => void;
  resumeRotation: () => void;
  resetAppearance: () => void;
  resetView: () => void;
}

interface GlobeProps {
  countriesData?: any;
  onCountrySelected?: (country: any) => void;
  isSearchSelection?: boolean;
}

const GlobeComponent = forwardRef<GlobeRef, GlobeProps>(({ countriesData, onCountrySelected, isSearchSelection }, ref) => {
  const globeRef = useRef<any>(null);
  const selectedCountryRef = useRef<any>(null);
  const globeInstanceRef = useRef<any>(null);

  useImperativeHandle(ref, () => ({
    zoomToCountry: (country: any) => {
      if (globeRef.current && country) {
        // Calculate country center
        const coordinates = country.geometry.coordinates;
        let totalLat = 0, totalLng = 0, pointCount = 0;
        
        const processCoords = (coords: any) => {
          if (Array.isArray(coords[0])) {
            if (typeof coords[0][0] === 'number') {
              coords.forEach((coord: any) => {
                if (Array.isArray(coord) && coord.length >= 2) {
                  totalLng += coord[0];
                  totalLat += coord[1];
                  pointCount++;
                }
              });
            } else {
              coords.forEach((subCoords: any) => processCoords(subCoords));
            }
          }
        };
        
        processCoords(coordinates);
        
        if (pointCount > 0) {
          const centerLat = totalLat / pointCount;
          const centerLng = totalLng / pointCount;
          
          // Zoom to country
          globeRef.current.pointOfView({ lat: centerLat, lng: centerLng, altitude: 1.5 }, 2000);
        }
      }
    },
    selectCountry: (country: any, isSearchSelection?: boolean) => {
      if (globeRef.current && country) {
        // Store the selected country
        selectedCountryRef.current = country;
        
        // Calculate country center for zoom
        const coordinates = country.geometry.coordinates;
        let totalLat = 0, totalLng = 0, pointCount = 0;
        
        const processCoords = (coords: any) => {
          if (Array.isArray(coords[0])) {
            if (typeof coords[0][0] === 'number') {
              coords.forEach((coord: any) => {
                if (Array.isArray(coord) && coord.length >= 2) {
                  totalLng += coord[0];
                  totalLat += coord[1];
                  pointCount++;
                }
              });
            } else {
              coords.forEach((subCoords: any) => processCoords(subCoords));
            }
          }
        };
        
        processCoords(coordinates);
        
        if (pointCount > 0) {
          const centerLat = totalLat / pointCount;
          const centerLng = totalLng / pointCount;
          
          // Zoom to country
          globeRef.current.pointOfView({ lat: centerLat, lng: centerLng, altitude: 1.5 }, 2000);
          
          // Stop auto-rotation when country is selected
          globeRef.current.controls().autoRotate = false;
          
          // Add pop-out effect with enhanced altitude and color
          setTimeout(() => {
            globeRef.current.polygonAltitude((d: any) => {
              if (d === country) return 0.15; // Pop out the selected country
              return 0.02; // Keep others at base level
            });
            
            globeRef.current.polygonCapColor((d: any) => {
              if (d === country) return '#F2F37F'; // New yellow highlight for selected
              return '#CFDECB'; // Default land color for others
            });
            
            globeRef.current.polygonSideColor((d: any) => {
              if (d === country) return 'rgba(242, 243, 127, 0.3)'; // New yellow sides for selected
              return 'rgba(207, 222, 203, 0.1)'; // Default land sides
            });
            
            // Update the landmark indicator
            globeRef.current.polygonLabel((d: any) => {
              if (d === country) {
                return `
                  <div style="
                    background: white;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 4px solid #ff6b35;
                    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 24px;
                    font-weight: bold;
                    color: #ff6b35;
                    position: relative;
                    animation: pulse 2s infinite;
                  ">
                    📍
                  </div>
                  <style>
                    @keyframes pulse {
                      0% { transform: scale(1); }
                      50% { transform: scale(1.1); }
                      100% { transform: scale(1); }
                    }
                  </style>
                `;
              }
              return '';
            });
            
            // Only notify parent component if this is NOT a search selection
            // Search selections should show confirmation modal instead
            setTimeout(() => {
              console.log('Globe selectCountry timeout - isSearchSelection param:', isSearchSelection, 'prop:', isSearchSelection, 'onCountrySelected:', !!onCountrySelected);
              if (onCountrySelected && !isSearchSelection) {
                console.log('Calling onCountrySelected from selectCountry');
                onCountrySelected(country);
              } else {
                console.log('Not calling onCountrySelected - search selection or no callback');
              }
            }, 300); // Wait for pop-out animation to complete
          }, 600); // Start pop-out effect after zoom begins
        }
      }
    },
    resumeRotation: () => {
      if (globeInstanceRef.current) {
        globeInstanceRef.current.controls().autoRotate = true;
        globeInstanceRef.current.controls().autoRotateSpeed = 0.2;
      }
    },
    resetView: () => {
      if (globeInstanceRef.current) {
        globeInstanceRef.current.pointOfView({ altitude: 1.8 }, 2000);
      }
    },
    resetAppearance: () => {
      if (globeInstanceRef.current) {
        console.log('Resetting globe appearance...');
        // Reset all visual effects
        globeInstanceRef.current.polygonAltitude(() => 0.02);
        globeInstanceRef.current.polygonCapColor(() => '#CFDECB');
        globeInstanceRef.current.polygonSideColor(() => 'rgba(207, 222, 203, 0.1)');
        globeInstanceRef.current.polygonLabel(() => '');
        selectedCountryRef.current = null;
        console.log('Globe appearance reset - extrusion effects removed');
        
        // Force a refresh of the globe to ensure changes are applied
        globeInstanceRef.current.polygonsData(globeInstanceRef.current.polygonsData());
      } else {
        console.log('Globe instance not found for reset');
      }
    },
  }));

  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Dynamically import Globe only on client side
      import('globe.gl').then((Globe) => {
        const globe = new Globe.default(globeRef.current);
        
        // Configure globe appearance with custom colors
        globe.backgroundColor('#D8DFE9');
        // Use a completely white globe texture
        globe.globeImageUrl('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjA0OCIgaGVpZ2h0PSIxMDI0IiB2aWV3Qm94PSIwIDAgMjA0OCAxMDI0IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cmVjdCB3aWR0aD0iMjA0OCIgaGVpZ2h0PSIxMDI0IiBmaWxsPSIjZmZmZmZmIi8+CjxjaXJjbGUgY3g9IjEwMjQiIGN5PSI1MTIiIHI9IjUxMiIgZmlsbD0iI2ZmZmZmZiIvPgo8L3N2Zz4K');
        globe.atmosphereColor('#ffffff'); // White atmosphere/halo
        globe.atmosphereAltitude(0.15); // Make atmosphere more visible
        globe.pointOfView({ altitude: 1.8 }, 0);
        
        // Use only ambient light for completely uniform illumination
        setTimeout(() => {
          const scene = globe.scene();
          scene.children.forEach((child: any) => {
            if (child.type === 'AmbientLight') {
              child.intensity = 10.0; // Extremely intense ambient light for completely uniform white
            }
            if (child.type === 'DirectionalLight') {
              child.intensity = 0; // Completely disable directional light
            }
          });
        }, 100);
        
        // Custom color scheme
        globe.polygonCapColor(() => '#CFDECB'); // Land color
        globe.polygonSideColor(() => 'rgba(207, 222, 203, 0.1)'); // Land side color
        globe.polygonStrokeColor(() => 'rgba(207, 222, 203, 0.3)'); // Land stroke color
        globe.polygonAltitude(() => 0.02); // Fixed: Set proper base altitude
        
        // Landmark-style indicator for selected countries
        globe.polygonLabel(({ properties: d }: any) => {
          // Only show landmark for selected country
          if (selectedCountryRef.current && d === selectedCountryRef.current) {
            return `
              <div style="
                background: white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 4px solid #ff6b35;
                box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 24px;
                font-weight: bold;
                color: #ff6b35;
                position: relative;
                animation: pulse 2s infinite;
              ">
                📍
              </div>
              <style>
                @keyframes pulse {
                  0% { transform: scale(1); }
                  50% { transform: scale(1.1); }
                  100% { transform: scale(1); }
                }
              </style>
            `;
          }
          return '';
        });

        // Smooth auto-rotate with gentle speed
        globe.controls().autoRotate = true;
        globe.controls().autoRotateSpeed = 0.2;
        
        // Enhanced hover effects with smooth transitions
        globe.polygonsTransitionDuration(300);
        globe.onPolygonHover((hoverD: any, prevHoverD: any) => {
          // Don't apply hover effects if there's a selected country
          if (selectedCountryRef.current) {
            return;
          }
          
          if (hoverD) {
            globe.polygonAltitude((d: any) => d === hoverD ? 0.05 : 0.02);
            globe.polygonCapColor((d: any) => d === hoverD ? '#ABC8F1' : '#CFDECB');
          } else {
            globe.polygonAltitude(() => 0.02);
            globe.polygonCapColor(() => '#CFDECB');
          }
        });

        // Handle direct clicks on countries
        globe.onPolygonClick((clickedCountry: any) => {
          if (clickedCountry && onCountrySelected) {
            console.log('Country clicked:', clickedCountry.properties.ADMIN || clickedCountry.properties.NAME);
            // Store the clicked country and trigger the selection effects
            selectedCountryRef.current = clickedCountry;
            
            // Apply the same visual effects as selectCountry
            const coordinates = clickedCountry.geometry.coordinates;
            let totalLat = 0, totalLng = 0, pointCount = 0;
            
            const processCoords = (coords: any) => {
              if (Array.isArray(coords[0])) {
                if (typeof coords[0][0] === 'number') {
                  coords.forEach((coord: any) => {
                    if (Array.isArray(coord) && coord.length >= 2) {
                      totalLng += coord[0];
                      totalLat += coord[1];
                      pointCount++;
                    }
                  });
                } else {
                  coords.forEach((subCoords: any) => processCoords(subCoords));
                }
              }
            };
            
            processCoords(coordinates);
            
            if (pointCount > 0) {
              const centerLat = totalLat / pointCount;
              const centerLng = totalLng / pointCount;
              
              // Zoom to country
              globe.pointOfView({ lat: centerLat, lng: centerLng, altitude: 1.5 }, 2000);
              
              // Stop auto-rotation
              globe.controls().autoRotate = false;
              
              // Add pop-out effect immediately (no delay)
              globe.polygonAltitude((d: any) => {
                if (d === clickedCountry) return 0.15; // Pop out the selected country
                return 0.02; // Keep others at base level
              });
              
              globe.polygonCapColor((d: any) => {
                if (d === clickedCountry) return '#F2F37F'; // Yellow highlight for selected
                return '#CFDECB'; // Default land color for others
              });
              
              globe.polygonSideColor((d: any) => {
                if (d === clickedCountry) return 'rgba(242, 243, 127, 0.3)'; // Yellow sides for selected
                return 'rgba(207, 222, 203, 0.1)'; // Default land sides
              });
              
              // Add the landmark indicator
              globe.polygonLabel((d: any) => {
                if (d === clickedCountry) {
                  return `
                    <div style="
                      background: white;
                      border-radius: 50%;
                      width: 50px;
                      height: 50px;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      border: 4px solid #ff6b35;
                      box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
                      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                      font-size: 24px;
                      font-weight: bold;
                      color: #ff6b35;
                      position: relative;
                      animation: pulse 2s infinite;
                    ">
                      📍
                    </div>
                    <style>
                      @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                        100% { transform: scale(1); }
                      }
                    </style>
                  `;
                }
                return '';
              });
            }
            
            onCountrySelected(clickedCountry);
          }
        });
        
        // Store globe instance for zoom functionality
        globeRef.current = globe;
        globeInstanceRef.current = globe;
        
        // Configure country polygons when data is available
        if (countriesData && countriesData.features) {
          globe.polygonsData(countriesData.features.filter((d: any) => d.properties.ISO_A2 !== 'AQ'));
        }
      });
    }
  }, [countriesData]);

  return (
    <div 
      ref={globeRef}
      className="w-full h-full"
      style={{ 
        width: '100%', 
        height: '100%',
        borderRadius: '16px',
        overflow: 'hidden',
        background: '#ffffff'
      }}
    />
  );
});

GlobeComponent.displayName = 'GlobeComponent';

export default GlobeComponent;