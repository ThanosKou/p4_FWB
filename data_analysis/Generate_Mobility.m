function s_mobility = Generate_Mobility(s_input)
% Copyright (c) 2011, Mathieu Boutin
% All rights reserved.
% 
% Redistribution and use in source and binary forms, with or without
% modification, are permitted provided that the following conditions are
% met:
% 
%     * Redistributions of source code must retain the above copyright
%       notice, this list of conditions and the following disclaimer.
%     * Redistributions in binary form must reproduce the above copyright
%       notice, this list of conditions and the following disclaimer in
%       the documentation and/or other materials provided with the distribution
% 
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
% AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
% IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
% ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
% LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
% CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
% SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
% INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
% CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
% ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
% POSSIBILITY OF SUCH DAMAGE.

    %The Random Waypoint mobility model.
    global s_mobility_tmp;
    global nodeIndex_tmp;
    
    s_mobility.NB_NODES = s_input.NB_NODES;
    s_mobility.SIMULATION_TIME = s_input.SIMULATION_TIME;
    for nodeIndex_tmp = 1:s_mobility.NB_NODES
        %%%%%%%%%%%%%%%%%%%%%%%%%%%Initialize:
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_IS_MOVING = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).dist_BS = [];

        previousX = 0;
        previousY = 0;
        previousDuration = 0;
        previousTime = 0;
        BS1_pos = s_input.BS1_POSITION;
        BS2_pos = s_input.BS2_POSITION;
        dst_id = 1;
        
        Out_setRestrictedWalk_random_waypoint(previousX,previousY,previousDuration,previousTime,s_input);

        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%Promenade     
        while (s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end) < s_input.SIMULATION_TIME)
            previousX = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X(end);
            previousY = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y(end);
            previousDuration = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(end);
            previousTime = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end);
            previousSpeed = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(end);
            previousDirection = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION(end);
            if (s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_IS_MOVING(end) == false)% now we are moving   
                Out_setRestrictedWalk_random_waypoint(previousX,previousY,previousDuration,previousTime,s_input);
            else
                %%%%%%%%Node is taking a pause:
                distance = previousDuration*previousSpeed;
                %%%
                dist_BS1 = norm([previousX previousY]- BS1_pos);
                dist_BS2 = norm([previousX previousY]- BS2_pos);
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).dist_BS(end+1,1) = dist_BS1;
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).dist_BS(end,2) = dist_BS2;
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).dist_BS(end,3) = previousDuration;
                
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end+1,1) = previousTime + previousDuration;
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X(end+1,1) = (previousX + distance*cosd(previousDirection));
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y(end+1,1) = (previousY + distance*sind(previousDirection));
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION(end+1,1) = 0;
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(end+1,1) = 0;
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_IS_MOVING(end+1,1) = false;
                s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(end+1,1) = Out_adjustDuration_random_waypoint(s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end),unifrnd(s_input.V_PAUSE_INTERVAL(1),s_input.V_PAUSE_INTERVAL(2)),s_input);
            end
        end
        %%%%%%%%%%%%%%%%%%To have speed vectors as well rather than
        %%%%%%%%%%%%%%%%%%only the scalar value:
        nb_speed = length(s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE);
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_X = zeros(nb_speed,1);
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_Y = zeros(nb_speed,1);
        for s = 1:nb_speed
            speed = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(s);
            direction = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION(s);
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_X(s) = speed*cosd(direction);
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_Y(s) = speed*sind(direction);
        end

        %%%%%%%%%%%%%%%%%%To remove null pauses:
        v_index = s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(1:end-1) == 0;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_IS_MOVING(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_X(v_index) = [];
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_Y(v_index) = [];

        %%%%%%%%%%%%%%%%%%To remove the too small difference at the end, if
        %%%%%%%%%%%%%%%%%%there is one:
        if ((s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end) - s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end-1)) < 1e-14)
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_IS_MOVING(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_X(end) = [];
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_Y(end) = [];
        end
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end) = s_input.SIMULATION_TIME;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(end) = 0;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(end) = 0;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_X(end) = 0;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_Y(end) = 0;
        
        s_mobility.VS_NODE(nodeIndex_tmp) = struct('V_TIME',s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME,...
                                              'V_POSITION_X',s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X,...
                                              'V_POSITION_Y',s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y,...
                                              'V_SPEED_X',s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_X,...
                                              'V_SPEED_Y',s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_Y,...
                                              'dist_BS',s_mobility_tmp.VS_NODE(nodeIndex_tmp).dist_BS);

    end
    
    clear s_mobility_tmp;
    clear nodeIndex_tmp;
end

function Out_setRestrictedWalk_random_waypoint(previousX,previousY,previousDuration,previousTime,s_input)

    global s_mobility_tmp;
    global nodeIndex_tmp;

    x_tmp = previousX;
    y_tmp = previousY;
    time_tmp = previousTime + previousDuration;
    duration_tmp = Out_adjustDuration_random_waypoint(time_tmp,unifrnd(s_input.V_WALK_INTERVAL(1),s_input.V_WALK_INTERVAL(2)),s_input);
    direction_tmp = unifrnd(s_input.V_DIRECTION_INTERVAL(1),s_input.V_DIRECTION_INTERVAL(2));
    speed = unifrnd(s_input.V_SPEED_INTERVAL(1),s_input.V_SPEED_INTERVAL(2));
    distance_tmp = speed*duration_tmp;
    if (distance_tmp == 0)
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end+1,1) = time_tmp;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X(end+1,1) =  x_tmp;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y(end+1,1) =  y_tmp;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION(end+1,1) = direction_tmp;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(end+1,1) = speed;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_IS_MOVING(end+1,1) = true;
        s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(end+1,1) = duration_tmp;
    else
        %The loop begins:
        flag_mobility_finished = false;
        while (~flag_mobility_finished)
            x_dest = x_tmp + distance_tmp*cosd(direction_tmp);
            y_dest = y_tmp + distance_tmp*sind(direction_tmp);
            flag_mobility_was_outside = false;
            if (x_dest > s_input.V_POSITION_X_INTERVAL(2))
                flag_mobility_was_outside = true;
                new_direction = 180 - direction_tmp;
                x_dest = s_input.V_POSITION_X_INTERVAL(2);
                y_dest = y_tmp + diff([x_tmp x_dest])*tand(direction_tmp);  
            end
            if (x_dest < s_input.V_POSITION_X_INTERVAL(1))
                flag_mobility_was_outside = true;
                new_direction = 180 - direction_tmp;
                x_dest = s_input.V_POSITION_X_INTERVAL(1);
                y_dest = y_tmp + diff([x_tmp x_dest])*tand(direction_tmp);
            end
            if (y_dest > s_input.V_POSITION_Y_INTERVAL(2))
                flag_mobility_was_outside = true;
                new_direction = -direction_tmp;
                y_dest = s_input.V_POSITION_Y_INTERVAL(2);
                x_dest = x_tmp + diff([y_tmp y_dest])/tand(direction_tmp); 
            end
            if (y_dest < s_input.V_POSITION_Y_INTERVAL(1))
                flag_mobility_was_outside = true;
                new_direction = -direction_tmp;
                y_dest = s_input.V_POSITION_Y_INTERVAL(1);
                x_dest = x_tmp + diff([y_tmp y_dest])/tand(direction_tmp);
            end
            current_distance = abs(diff([x_tmp x_dest]) + 1i*diff([y_tmp y_dest]));
            current_duration = Out_adjustDuration_random_waypoint(time_tmp,current_distance/speed,s_input);
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_TIME(end+1,1) = time_tmp;
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_X(end+1,1) = x_tmp;
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_POSITION_Y(end+1,1) = y_tmp;
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DIRECTION(end+1,1) = direction_tmp;
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_SPEED_MAGNITUDE(end+1,1) = speed;
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_IS_MOVING(end+1,1) = true;
            s_mobility_tmp.VS_NODE(nodeIndex_tmp).V_DURATION(end+1,1) = current_duration;
            if(flag_mobility_was_outside)
                time_tmp = time_tmp + current_duration;
                duration_tmp = duration_tmp - current_duration;
                distance_tmp = distance_tmp - current_distance;
                x_tmp = x_dest;
                y_tmp = y_dest;
                direction_tmp = new_direction;
            else
                flag_mobility_finished = true;
            end
        end
        %the loop ended
    end
end

function duration = Out_adjustDuration_random_waypoint(time,duration,s_input)

    if ((time+duration) >= s_input.SIMULATION_TIME)
        duration = s_input.SIMULATION_TIME - time;
    end
end