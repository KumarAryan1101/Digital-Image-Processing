clc;
clear;
close all;

% ============================================================
%             TAMBOLA / HOUSIE TICKET GENERATOR
% =============================================================
% Conditions:
% 1. Ticket size = 3 rows x 9 columns
% 2. Exactly 15 numbers
% 3. Exactly 5 numbers in every row
% 4. Every column contains at least 1 number
% 5. No column contains more than 3 numbers
% 6. Numbers in each column follow standard Tambola ranges
% 7. Numbers in each column are sorted from top to bottom
% 8. No repeated number in a ticket
% =============================================================

validPattern = false;

while ~validPattern

    % Randomly create a binary 3x9 matrix
    % 1 = number will be placed
    % 0 = blank
    pattern = rand(3,9) > 0.5;

    % Check row condition: exactly 5 numbers per row
    rowCount = sum(pattern,2);

    % Check column condition: 1 to 3 numbers per column
    colCount = sum(pattern,1);

    if all(rowCount == 5) && ...
       all(colCount >= 1) && ...
       all(colCount <= 3)

        validPattern = true;
    end
end

% Tambola number ranges

ranges = cell(1,9);

ranges{1} = 1:9;
ranges{2} = 10:19;
ranges{3} = 20:29;
ranges{4} = 30:39;
ranges{5} = 40:49;
ranges{6} = 50:59;
ranges{7} = 60:69;
ranges{8} = 70:79;
ranges{9} = 80:90;

% Create empty ticket

ticket = NaN(3,9);

% Fill each column

for c = 1:9

    rows = find(pattern(:,c));

    n = length(rows);

    % Randomly select required number of values
    availableNumbers = ranges{c};

    selectedNumbers = availableNumbers( ...
        randperm(length(availableNumbers),n));

    % Sort numbers in ascending order
    selectedNumbers = sort(selectedNumbers);

    % Put numbers into selected rows
    for k = 1:n
        ticket(rows(k),c) = selectedNumbers(k);
    end
end

disp(' ');
disp('======================================');
disp('          TAMBOLA TICKET');
disp('======================================');

disp(ticket);

hold on;
axis equal;

% Draw cells
for r = 1:3
    for c = 1:9

        % Cell position
        x = c-1;
        y = 3-r;

        % Draw rectangle
        rectangle( ...
            'Position',[x y 1 1], ...
            'EdgeColor','black', ...
            'LineWidth',2, ...
            'FaceColor',[0.95 0.95 0.95]);

        % Add number if present
        if ~isnan(ticket(r,c))

            text(x+0.5,y+0.5, ...
                num2str(ticket(r,c)), ...
                'HorizontalAlignment','center', ...
                'VerticalAlignment','middle', ...
                'FontSize',20, ...
                'FontWeight','bold');

        end
    end
end

xlim([0 9]);
ylim([0 3]);

set(gca, ...
    'XTick',[], ...
    'YTick',[], ...
    'Box','off');

title('TAMBOLA / HOUSIE TICKET', ...
    'FontSize',18, ...
    'FontWeight','bold');

hold off;