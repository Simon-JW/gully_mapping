clear all

tic

array = ones(1000, 1000);
%array = [1,2,3,4; 5,4,7,6; 9,2,3,4; 4,5,6,7];
%array = [1,2,3,4,3; 4,5,4,7,6; 5,9,2,3,4; 6,4,5,6,7; 6,4,5,6,7];
%array = [1,2,3,4,7,8; 5,4,7,6,6,7; 9,2,3,4,3,5; 3,4,5,6,6,7; 9,2,3,4,3,5; 3,4,5,6,6,7];
     
test = mean(mean(array))

window = 2%This should always be 2 as it works fastest.

columns = im2col(array, [window window]);

%each iteration increases the window dimension by 1 (even though it starts
%as a 2 x 2)

window_size = 1 %This is different to the variable 'window' above.

for i = 1:window_size
    dim_1 = size(array,1);
    dim_2 = size(array,2);
    wind_mean = col2im(mean(columns), [window window], [dim_1 dim_2], 'slider');
    array = wind_mean;
    columns = im2col(array, [window window]);
end
toc

%%

tic                                                                                                                                                                                                                                                                                                                    
new_dims = length(wind_mean) * 2  + 1;

new = zeros(new_dims,new_dims);

for i = 1:size(wind_mean,1)
    for o = 1:size(wind_mean,2)
        new_index_i = i * 2;
        new_index_o = o * 2;
        new(new_index_i, new_index_o) = wind_mean(i,o);
    end
end

toc

%%
tic

%Deal with corners first.

%top left.

new(1,1) = new(2,2);
tl_row = num2str(1);
tl_col = num2str(1);
tl = strcat(tl_row, ',', tl_col);

%top right.

new(1,size(new,1)) = new(2, (size(new,1)-1));
tr_row = num2str(1);
tr_col = num2str(size(new,2));
tr = strcat(tr_row, ',', tr_col);

%bottom left.

new(size(new,2), 1) = new((size(new,2)-1), 2);
bl_row = num2str(size(new,2));
bl_col = num2str(1);
bl = strcat(bl_row, ',', bl_col);

%bottom right.

new(size(new,2), size(new,1)) = new((size(new,2)-1), (size(new,1)-1));
br_row = num2str(size(new,1));
br_col = num2str(size(new,2));
br = strcat(br_row, ',', br_col);


%Do the left edge.
tic
for row = 1:size(new, 1)
    for column = 1:size(new, 2)
        row_st = num2str(row);
        col_str = num2str(column);
        cell_str = strcat(row_st, ',', col_str);
        %cell_location = str2num(cell_str)
        if column ==  1 && strcmp(cell_str, tl) == 0  && strcmp(cell_str, bl) == 0 && mod(row, 2) == 1
            right_shift = column + 1;
            down_shift = row + 1;
            up_shift = row - 1;
            value_1 = new(down_shift,right_shift);
            value_2 = new(up_shift,right_shift);
            value = (value_1 + value_2) / 2;
            new(row,column) = value;
        else
        end
    end
end
toc

%Do the right edge.
tic
for row = 1:size(new, 1)
    for column = 1:size(new, 2)
        row_st = num2str(row);
        col_str = num2str(column);
        cell_str = strcat(row_st, ',', col_str);
        %cell_location = str2num(cell_str)
        if column ==  size(new,2) && strcmp(cell_str, tr) == 0  && strcmp(cell_str, br) == 0 && mod(row, 2) == 1
            left_shift = column - 1;
            down_shift = row + 1;
            up_shift = row - 1;
            value_1 = new(down_shift,left_shift);
            value_2 = new(up_shift,left_shift);
            value = (value_1 + value_2) / 2;
            new(row,column) = value;
        else
        end
    end
end
toc
%Do the top.
tic
for row = 1:size(new, 1)
    for column = 1:size(new, 2)
        row_st = num2str(row);
        col_str = num2str(column);
        cell_str = strcat(row_st, ',', col_str);
        %cell_location = str2num(cell_str)
        if row ==  1 && strcmp(cell_str, tl) == 0  && strcmp(cell_str, tr) == 0 && mod(row, 2) == 1
            left_shift = column - 1;
            right_shift = column + 1;
            down_shift = row + 1;
            value_1 = new(down_shift,left_shift);
            value_2 = new(down_shift,right_shift);
            value = (value_1 + value_2) / 2;
            new(row,column) = value;
        else
        end
    end
end
toc
%Do bottom.
tic
for row = 1:size(new, 1)
    for column = 1:size(new, 2)
        row_st = num2str(row);
        col_str = num2str(column);
        cell_str = strcat(row_st, ',', col_str);
        %cell_location = str2num(cell_str)
        if row ==  size(new,2) && strcmp(cell_str, bl) == 0  && strcmp(cell_str, br) == 0 && mod(row, 2) == 1
            left_shift = column - 1;
            right_shift = column + 1;
            up_shift = row - 1;
            value_1 = new(up_shift,left_shift);
            value_2 = new(up_shift,right_shift);
            value = (value_1 + value_2) / 2;
            new(row,column) = value;
        else
        end
    end
end

%Now do the rest.

for row = 1:size(new, 1)
    for column = 1:size(new, 2)
        row_st = num2str(row);
        col_str = num2str(column);
        cell_str = strcat(row_st, ',', col_str);
        %cell_location = str2num(cell_str)
        if row ~=  size(new,1) && row ~=  1 && column ~= size(new,2) && column ~= 1 && mod(row, 2) == 1 && mod(column, 2) == 1;
            left_shift = column - 1;
            right_shift = column + 1;
            up_shift = row - 1;
            down_shift = row + 1;
            value_1 = new(up_shift,left_shift);
            value_2 = new(up_shift,right_shift);
            value_3 = new(down_shift,left_shift);
            value_4 = new(down_shift,right_shift);
            value = (value_1 + value_2 + value_3 + value_4) / 4;
            new(row,column) = value;
        else
        end
    end
end
toc
%%

%Cut out middle row and middle column.

a = linspace(2,size(new,1) - 1 ,size(array, 1))
%%
new(:, a) = [];
new_subset(mid_row, :) = [];


toc



