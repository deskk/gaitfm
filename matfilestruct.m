function print_mat_structure(mat_file)
    % Load .mat file
    data = load(mat_file);
    fprintf('File Structure of: %s\n', mat_file);
    displayStructFields(data, '');
end

function displayStructFields(s, prefix)
    % Recursively print structure fields
    fields = fieldnames(s);
    for i = 1:numel(fields)
        field = fields{i};
        value = s.(field);
        field_path = sprintf('%s%s', prefix, field);
        
        % Check if it's a structure
        if isstruct(value)
            fprintf('%s (struct)\n', field_path);
            displayStructFields(value, [field_path '.']); % Recursive call
        else
            % Print size and type of the field
            sz = size(value);
            fprintf('%s (%s) - Size: [%s]\n', field_path, class(value), num2str(sz));
        end
    end
end

print_mat_structure('data/SUB01.mat')
