header = '''
$HEADER$
uniform vec2 resolution;
uniform float time;
uniform vec2 mouse;
'''


shader_watter_bubble = header + '''
void main(void)
{
    vec2 halfres = resolution.xy / 2.0;
    vec2 cpos = vec4(frag_modelview_mat * gl_FragCoord).xy;

    vec2 sinres = vec2(tan(resolution.x * time), -sin(resolution * time));

    cpos.x -= 0.5 * halfres.x * sin(time/2.0) + \
        0.3 * halfres.x * cos(time) + halfres.x;

    cpos.y -= 0.5 * halfres.y * sin(time/5.0) + \
        0.3 * halfres.y * sin(time) + halfres.y;

    float cLength = length(cpos);

    vec2 uv = \
        tex_coord0 + (cpos / cLength) * \
            sin(cLength / 50.0 - time * 2.0) / 15.0;

    vec3 col = texture2D(texture0, uv).xyz;
    gl_FragColor = vec4(col, 1.0);
}
'''
