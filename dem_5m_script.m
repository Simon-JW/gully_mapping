clear all 
close all

data_dir='C:\DEM_5m';
cd(data_dir)
dir
%%

tic
data = imread('don_5m.tif');
data = double(data);
min = min(min(data));
data(data == min) = NaN;
toc

%%
tic
%Setup the desired specifications.

elevation_max = 100 %This is in meters and will chop off anything above this height.

window_size = 20 %This is the number of pixels along eac haxis of the window.

%Set the desired function. Min, max, median, std... whatever. Better to
%just create a bunch of functions and then just apply desired one.

fun_mean = @(x) mean(x(:)); 
fun_std = @(x) std(x(:)); 
fun_min = @(x) min(x(:)); 
fun_max = @(x) max(x(:)); 
fun_var = @(x) var(x(:)); 
fun_mode = @(x) mode(x(:)); 

toc

%%
%How to use prctile.

a = randi([1 100], 10) % Random test matrix of size 10 x 10.

b = prctile(a,90)

c = a == b %Creates a mask where values above specified prctile == 1 else 0.

%Then multiply the mask over the top of the original data.

%%
%Subset the by creating a new layer with the high elevation removed (and potentially any additional arguments against
% variable 'subset'.
tic

subset = data;

subset(subset > elevation_max) = NaN;%Removing all higher elevation from the analysis.

I2 = nlfilter(subset,[window_size window_size],fun_mean);%Using a filer of specified window size and applying the function defined at the top.

I3 = nlfilter(subset,[window_size window_size],fun_std);%Using a filer of specified window size and applying the function defined at the top.

toc

figure(1); 
h = imagesc(data); 
set(h,'alphadata', ~isnan(data))
axis off; axis equal; ylabel(colorbar, 'meters'); 
title('Fitzroy 5m DEM'); colormap(flipud(Golds))


standard_anomaly_grid = (subset - I2)./I3;%Combining the two window operations above allows me t ocalculate a standardised anomaly.

figure(1); 
h = imagesc(standard_anomaly_grid, [-2 -0.5]); 
set(h,'alphadata', ~isnan(standard_anomaly_grid))
axis off; axis equal; ylabel(colorbar, 'standardised anomaly (meters)'); 
title('Fitzroy 5m DEM'); colormap(TealBrown)

%Create a contiguity mask and then apply it to "grid_minus_mean".

%%
contiguity = standard_anomaly_grid > -2 & standard_anomaly_grid < -0.7;

figure(1); 
h = imagesc(contiguity); 
set(h,'alphadata', ~isnan(contiguity))
axis off; axis equal; ylabel(colorbar, 'meters'); 
title('Fitzroy 5m DEM'); colormap(Brown)

BW2 = bwareaopen(contiguity, 40);


figure(2); 
h = imagesc(BW2); 
set(h,'alphadata', ~isnan(BW2))
axis off; axis equal; ylabel(colorbar, 'meters'); 
title('Fitzroy 5m DEM'); colormap(Brown)

%%
%Apply mask.

masked = BW2 .* standard_anomaly_grid;


figure(3); 
h = imagesc(masked); 
set(h,'alphadata', ~isnan(masked))
axis off; axis equal; ylabel(colorbar, 'meters'); 
title('Fitzroy 5m DEM'); colormap(flipud(Golds))


%%
%Generate size distribution of binary objects.

t = regionprops('table', BW2, 'Area')
figure
histogram(t.Area)
title('Object size distribution')

%%
%Filter testing.

%Fuck yeah!!!! this is sooo much better.

abc = [1,2,3,4,5;
       6,7,8,9,10;
       11,12,13,14,15;
       16,17,18,19,20;
       21,22,23,24,25]
   
abc(2,5) = NaN

fun = @(x) mean(x(:)); 

I2 = nlfilter(abc,[3 3],fun)
