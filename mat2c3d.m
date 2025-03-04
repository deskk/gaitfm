clc; clear; close all;

%% ---- STEP 1: Load .mat File ----
mat_file = 'data/SUB01.mat'; % Change to your actual .mat filename
data = load(mat_file);

%% ---- STEP 2: Find All Subjects & Conditions ----
subject_names = fieldnames(data);

for i = 1:numel(subject_names)
    subject = subject_names{i};
    subject_data = data.(subject);
    
    condition_names = fieldnames(subject_data);
    
    for j = 1:numel(condition_names)
        condition = condition_names{j};
        condition_data = subject_data.(condition);
        
        % Iterate over stiffness conditions
        stiffness_names = fieldnames(condition_data);
        for k = 1:numel(stiffness_names)
            stiffness = stiffness_names{k};
            stiffness_data = condition_data.(stiffness);
            
            % ---- STEP 3: Extract Marker Data ----
            if isfield(stiffness_data, 'markers')
                marker_struct = stiffness_data.markers; % Extract marker struct
                
                % Convert marker struct to numerical array
                marker_fields = fieldnames(marker_struct);
                numFrames = numel(marker_struct.(marker_fields{1})); % Number of frames
                numMarkers = numel(marker_fields); % Number of markers
                
                % Preallocate marker data (Frames x Markers x XYZ)
                markers = nan(numFrames, numMarkers, 3);
                
                for m = 1:numMarkers
                    marker_name = marker_fields{m};

                    marker_values = marker_struct.(marker_name); % extract marker data

                    % convert cell to numeric
                    if iscell(marker_values)
                        marker_values = cell2mat(marker_values);
                    end
                    % assert correct size before storing
                    if size(marker_values, 1) == numFrames && size(marker_values, 2) == 3
                        markers(:,m,:) = reshape(marker_values, numFrames,1,3);
                    else
                        warning('skipping marker %s: incorrect dimensions [%d x %d]', marker_name, size(marker_values,1), size(marker_values,2));
                        continue;
                    end
                end
            else
                warning('skip %s-%s-%s (no marker data found)\n', subject, condition, stiffness);
                continue;
            end
            % ---- STEP 4: Extract Time Data ----
            if isfield(stiffness_data, 'time') && isfield(stiffness_data.time, 'time')
                time = stiffness_data.time.time; % Extract time vector
            else
                fprintf('Skipping %s-%s-%s (No time data found)\n', subject, condition, stiffness);
                continue;
            end
            
            %% ---- STEP 5: Convert to C3D ----
            h = btkNewAcquisition();
            btkSetFrameNumber(h, numFrames);
            btkSetPointNumber(h, numMarkers);
            btkSetFrequency(h, 1 / mean(diff(time))); % Compute sampling rate
            
            % Add Marker Data
            for m = 1:numMarkers
                markerName = sprintf('Marker_%d', m);
                btkAppendPoint(h, markerName, squeeze(markers(:, m, :)), 'marker');
            end
            
            % Save C3D File
            c3d_filename = sprintf('%s_%s_%s.c3d', subject, condition, stiffness);
            btkWriteAcquisition(h, c3d_filename);
            btkCloseAcquisition(h);
            
            fprintf('Converted %s -> %s\n', subject, condition, c3d_filename);
        end
    end
end

disp('complete')