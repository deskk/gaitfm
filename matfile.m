clc; clear; close all;

mat_file = 'data/SUB01.mat';
data = load(mat_file);

% function print all fields
function displayStructFields(s, prefix)
    if nargin < 2
        prefix = ''; % Root level
    end
    fields = fieldnames(s);
    for i = 1:numel(fields)
        field = fields{i};
        value = s.(field);
        if isstruct(value)
            fprintf('%s%s (struct)\n', prefix, field);
            displayStructFields(value, [prefix field '.']); % Recursive call
        else
            fprintf('%s%s (%s)\n', prefix, field, class(value));
        end
    end
end

disp('variables in mat file:');
disp(fieldnames(data))
%displayStructFields(data);