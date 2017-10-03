%Textural analysis.
clear all
close all
clc

data_dir='C:\PhD\junk\';
cd(data_dir)
dir

file = imread('quantv3.tif');

%%
subset = double(file(10300:12700, 9400:10800));

subset(subset<0)=NaN;

figure(1); 
h = imagesc(subset); 
set(h,'alphadata', ~isnan(subset))
axis off; axis equal; ylabel(colorbar, 'Category'); 
title('Land use map'); colormap(flipud(jet));

%%
%Test marix.
I = [1,8,5,0;
    1,1,7,1;
    0,1,0,6;
    2,1,0,2];

I2 = [1 1 5 6 8; 
    2 3 5 7 1; 
    4 5 7 1 2; 
    8 5 1 2 5]

%%
[glcms, SI] =  graycomatrix(subset,'NumLevels',9,'GrayLimits',[]);
glcms(1,1)